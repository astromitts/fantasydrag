from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError
from django.db.models import Q
from flags.models import FeatureFlag

from fantasydrag.models import (
    AppearanceType,
    Draft,
    DragRace,
    DragRaceType,
    DefaultRule,
    Episode,
    EpisodeDraft,
    Panel,
    Participant,
    Queen,
    Score,
    WildCardAppearance,
)
from fantasydrag.api.serializers import (
    AppearanceSerializer,
    AppearanceTypeSerializer,
    DraftSerializer,
    DragRaceSerializer,
    DragRaceSerializerMeta,
    EpisodeScore,
    EpisodeDraftSerializer,
    EpisodeDraftSerializerShort,
    EpisodeSerializerShort,
    PanelSerializer,
    PanelSerializerMeta,
    ParticipantSerializer,
    QueenSearchSerializer,
    QueenSerializer,
    RuleSerializer,
    ScoreSerializer,
    UserSerializer,
    WQDraftSerializer,
    StatSerializer,
)
from fantasydrag.stats import Stats
from fantasydrag.utils import refresh_dragrace_stats_for_participant


def get_available_queens(view, participant):
    participant_drafts = view.panel.draft_set.filter(participant=participant)
    drafted_queens = [pd.queen for pd in participant_drafts]

    queens_by_draft_count = {}
    for draft in view.panel.draft_set.all():
        this_count = queens_by_draft_count.get(draft.queen, 0)
        this_count += 1
        queens_by_draft_count[draft.queen] = this_count

    available_queens = []
    for queen in view.panel.drag_race.queens.all():
        if queens_by_draft_count.get(queen, 0) < view.panel.queen_draft_allowance and queen not in drafted_queens:  # noqa
            available_queens.append(queen)
    return available_queens


def get_serialized_available_queens(view, participant):
    available_queens = get_available_queens(view, participant)
    available_queens_serialized = QueenSerializer(instance=available_queens, many=True)
    available_queens_data = available_queens_serialized.data
    return available_queens_data


def get_available_wq_queens(view, participant):
    participant_drafts = view.panel.wildcardqueen_set.filter()
    drafted_queens = [pd.queen for pd in participant_drafts]
    season_queens = view.panel.drag_race.queens.all()
    unavailable_queens = drafted_queens + [q for q in season_queens]

    available_queens = Queen.objects.exclude(pk__in=[uq.pk for uq in unavailable_queens])

    return available_queens


def get_serialized_available_wq_queens(view, participant):
    available_queens = get_available_wq_queens(view, participant)
    available_queens_serialized = QueenSerializer(instance=available_queens, many=True)
    available_queens_data = available_queens_serialized.data
    return available_queens_data


def get_draft_data(view, response_status='ok', response_message=None):
    panel_data = PanelSerializer(instance=view.panel, many=False).data
    participants = []
    if view.panel.draft_order:
        for participant_order in view.panel.draft_order:
            participant = view.panel.participants.get(pk=participant_order)
            participant_data = ParticipantSerializer(instance=participant, many=False).data

            wq_drafts = view.panel.wildcardqueen_set.filter(participant=participant).order_by('queen__name').all()
            wq_drafts_data = WQDraftSerializer(instance=wq_drafts, many=True).data

            drafts = view.panel.draft_set.filter(participant=participant).order_by('round_selected').all()
            drafts_data = DraftSerializer(instance=drafts, many=True).data

            if view.panel.status == 'in draft':
                participant_available_queens = get_serialized_available_queens(view, participant)
            elif view.panel.status == 'wildcards':
                participant_available_queens = get_serialized_available_wq_queens(view, participant)
            else:
                participant_available_queens = None
            participants.append(
                {
                    'participant': participant_data,
                    'available_queens': participant_available_queens,
                    'wq_drafts': wq_drafts_data,
                    'drafts': drafts_data
                }
            )
    else:
        for participant in view.panel.participants.all():
            participant_data = ParticipantSerializer(instance=participant, many=False).data
            participant_available_queens = get_serialized_available_queens(view, participant)
            participants.append(
                {'participant': participant_data, 'available_queens': participant_available_queens}
            )

    panel_drafts = Draft.objects.filter(panel=view.panel).order_by('-round_selected', '-pk').all()
    drafts_data = DraftSerializer(instance=panel_drafts, many=True).data
    request_status = {
        'status': response_status,
        'message': response_message,
        'is_site_admin': view.is_site_admin,
        'is_captain': view.is_captain,
        'is_current_participant': view.is_current_participant,
        'request_participant': view.request_participant.pk,
    }
    return {
        'meta': request_status,
        'panel': panel_data,
        'participants': participants,
        'drafts': drafts_data,
    }


def setcontext(view, request):
    view.participant = Participant.objects.filter(user=request.user).first()
    if view.participant:
        view.response = {
            'user': {
                'is_authenticated': request.user.is_authenticated,
                'is_site_admin': view.participant.site_admin,
                'pk': view.participant.pk
            }
        }
    else:
        view.response = {
            'user': {
                'is_authenticated': request.user.is_authenticated,
                'is_site_admin': False
            }
        }


def set_user_context(view, request, panel_id):
    view.panel = Panel.objects.get(pk=panel_id)
    view.user = request.user
    view.request_participant = Participant.objects.get(user=view.user)
    view.is_site_admin = view.request_participant.site_admin
    view.is_captain = view.request_participant in view.panel.captains.all()
    view.is_current_participant = view.request_participant == view.panel.current_draft_player


class DragRaceApi(APIView):
    def get(self, request, *args, **kwargs):
        drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
        response = DragRaceSerializer(instance=drag_race)
        return Response(response.data)

    def _create_drag_race(self, request):
        status = 'ok'
        message = None
        drag_race_data = {}

        season = request.data['season']
        franchise = request.data['franchise']
        race_type = request.data['drag_race_type']

        try:
            drag_race = DragRace(
                season=season,
                franchise=franchise,
                drag_race_type=DragRaceType.objects.get(pk=race_type)
            )
            drag_race.save()

            for queen in request.data['queens']:
                if queen['pk']:
                    queen = Queen.objects.get(pk=queen['pk'])
                else:
                    queen = Queen(
                        name=queen['name'],
                        main_franchise=drag_race.franchise
                    )
                    try:
                        queen.save()
                    except IntegrityError:
                        queen = Queen.objects.get(name=queen['name'])
                drag_race.queens.add(queen)

            drag_race_data = DragRaceSerializer(instance=drag_race).data

            message = 'Created Drag Race {} {} season {}'.format(
                franchise, race_type, season
            )

        except IntegrityError:
            status = 'error'
            message = 'Drag Race {} {} season {} already exists'.format(
                franchise, race_type, season
            )
        response = {
            'status': status,
            'message': message,
            'drag_race': drag_race_data,
        }
        return response

    def _update_drag_race(self, request):
        drag_race = DragRace.objects.get(pk=request.data['pk'])

        status = 'ok'
        message = None
        drag_race_data = {}

        season = request.data['season']
        franchise = request.data['franchise']
        race_type = request.data['drag_race_type']

        try:
            drag_race.season = season
            drag_race.franchise = franchise
            drag_race.drag_race_type = DragRaceType.objects.get(pk=race_type)
            drag_race.save()
            current_queens = {q.pk: q for q in drag_race.queens.all()}
            posted_queens = {}
            for posted_queen in request.data['queens']:
                new_queen = posted_queen['pk'] is None
                if new_queen:
                    queen = Queen(
                        name=posted_queen['name'],
                        main_franchise=drag_race.franchise
                    )
                    try:
                        queen.save()
                    except IntegrityError:
                        queen = Queen.objects.get(name=posted_queen['name'])
                    drag_race.queens.add(queen)
                elif posted_queen['pk'] not in current_queens.keys():
                    queen = Queen.objects.get(pk=posted_queen['pk'])
                    drag_race.queens.add(queen)
                else:
                    queen = None
                    posted_queens[posted_queen['pk']] = {}
                if queen:
                    posted_queens[queen.pk] = queen

            for pk, queen in current_queens.items():
                if pk not in posted_queens:
                    drag_race.queens.remove(queen)

            message = 'Updated Drag Race {} {} season {}'.format(
                franchise, race_type, season
            )
        except IntegrityError:
            status = 'error'
            message = 'Drag Race {} {} season {} already exists'.format(
                franchise, race_type, season
            )

        drag_race_data = DragRaceSerializer(instance=drag_race).data
        response = {
            'status': status,
            'message': message,
            'drag_race': drag_race_data,
        }
        return response

    def post(self, request, *args, **kwargs):
        update = request.data['pk'] != 'None'
        if not update:
            response = self._create_drag_race(request)
        elif update:
            response = self._update_drag_race(request)
        return Response(response)


class EpisodeDraftApi(APIView):
    def setup_episode_panel(self, request, *args, **kwargs):
        self.episode = Episode.objects.get(pk=kwargs['episode_id'])
        self.participant = Participant.objects.get(user=request.user)
        self.episode_draft = EpisodeDraft.objects.filter(
            episode=self.episode, participant=self.participant).first()
        if not self.episode_draft:
            self.episode_draft = EpisodeDraft(
                episode=self.episode,
                participant=self.participant,
                drag_race=self.episode.drag_race
            )
            self.episode_draft.save()

    def get(self, request, *args, **kwargs):
        self.setup_episode_panel(request, *args, **kwargs)
        draft_data = EpisodeDraftSerializer(self.episode_draft).data
        return Response(draft_data)

    def post(self, request, *args, **kwargs):
        self.setup_episode_panel(request, *args, **kwargs)

        try:
            for queen in self.episode_draft.queens.all():
                self.episode_draft.queens.remove(queen)
            self.episode_draft.save()
            for queen in request.data['queens']:
                queen = Queen.objects.get(pk=queen['pk'])
                self.episode_draft.queens.add(queen)
            self.episode_draft.save()
            status = {
                'status': 'ok',
                'message': 'Panel saved!'
            }
        except:
            status = {
                'status': 'error',
                'message': 'An unkown error occurred. Please try again.'
            }
        return Response(status)


class AppearanceTypeApi(APIView):
    def get(self, request, *args, **kwargs):
        appearances = AppearanceType.objects.all()
        serializer = AppearanceTypeSerializer(instance=appearances, many=True)
        return Response(serializer.data)


class EpisodeAppearanceApi(APIView):
    def _setcontext(self, request, *args, **kwargs):
        self.episode = Episode.objects.get(pk=kwargs['episode_id'])

    def get(self, request, *args, **kwargs):
        self._setcontext(request, *args, **kwargs)
        appearances = WildCardAppearance.objects.filter(episode=self.episode).order_by('-pk').all()
        serializer = AppearanceSerializer(instance=appearances, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        self._setcontext(request, *args, **kwargs)
        appearance = AppearanceType.objects.get(pk=request.data['appearance'])
        queen = Queen.objects.get(pk=request.data['queen'])
        new_wqa = WildCardAppearance(
            appearance=appearance,
            queen=queen,
            episode=self.episode
        )
        new_wqa.save()
        response = AppearanceSerializer(instance=new_wqa, many=False)
        return Response(response.data)

    def delete(self, request, *args, **kwargs):
        self._setcontext(request, *args, **kwargs)
        WildCardAppearance.objects.get(pk=kwargs['wqa_id']).delete()
        return Response({'status': 'ok'})


class QueenApi(APIView):
    def get(self, request, *args, **kwargs):
        queens = Queen.objects.all()
        serializer = QueenSerializer(instance=queens, many=True)
        return Response(serializer.data)


class QueenSearchApi(APIView):
    def get(self, request, *args, **kwargs):
        queens = Queen.objects.all()
        serializer = QueenSearchSerializer(instance=queens, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """ Examples
        {
            "filters": {
                "franchise": "UK"
            }
        }
        """
        queens_qs = Queen.objects
        if request.data.get('filters'):
            filters = request.data['filters']
            if 'name' in filters:
                queens_qs = queens_qs.filter(
                    Q(normalized_name__icontains=filters['name']) | Q(name__icontains=filters['name'])

                )
            if 'franchise' in filters:
                queens_qs = queens_qs.filter(main_franchise=filters['franchise'])
        serializer = QueenSearchSerializer(instance=queens_qs.all(), many=True)
        return Response(serializer.data)


class DefaultRulesApi(APIView):
    def get(self, request, *args, **kwargs):
        rules = DefaultRule.objects.all()
        serializer = RuleSerializer(instance=rules, many=True)
        return Response(serializer.data)


class EpisodeApi(APIView):
    def get(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        serializer = EpisodeScore(instance=episode, many=False)
        response = serializer.data
        return Response(response)

    def put(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        queen = Queen.objects.get(pk=request.data['queen'])
        rule = DefaultRule.objects.get(pk=request.data['rule'])
        score = Score(
            episode=episode,
            default_rule=rule,
            queen=queen
        )
        score.save()
        serializer = ScoreSerializer(instance=score, many=False)
        response = serializer.data
        return Response(response)

    def patch(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        if 'is_scored' in request.data:
            episode.is_scored = request.data['is_scored']
        if 'has_aired' in request.data:
            episode.has_aired = request.data['has_aired']
        if 'title' in request.data:
            episode.title = request.data['title']
        episode.save()
        serializer = EpisodeScore(instance=episode, many=False)
        response = serializer.data
        return Response(response)

    def delete(self, request, *args, **kwargs):
        score = Score.objects.get(pk=kwargs['score_id'])
        score.delete()
        response = {'status': 'ok'}
        return Response(response)


class DraftMetaApi(APIView):
    def get(self, request, *args, **kwargs):
        set_user_context(self, request, kwargs['panel_id'])
        participant_drafts_data = get_draft_data(self)
        wq_drafts = self.panel.wildcardqueen_set.order_by('participant__user__username', 'pk').all()
        wq_drafts_data = WQDraftSerializer(instance=wq_drafts, many=True).data
        panel_drafts = Draft.objects.filter(panel=self.panel).order_by('-round_selected', '-pk').all()
        drafts_data = DraftSerializer(instance=panel_drafts, many=True).data

        if self.panel.current_draft_player:
            participant_pk = self.panel.current_draft_player.pk
        else:
            participant_pk = 0
        response = {
            'is_current_participant': self.is_current_participant,
            'request_participant': self.request_participant.pk,
            'participant_pk': participant_pk,
            'drafts': drafts_data,
            'wq_drafts': wq_drafts_data,
            'panel': {
                'status': self.panel.status,
                'round': self.panel.current_round
            },
            'participants': participant_drafts_data['participants'],
        }
        return Response(response)


class DraftAvailableQueensApi(APIView):
    def get(self, request, *args, **kwargs):
        set_user_context(self, request, kwargs['panel_id'])
        participants = []
        if self.panel.status == 'in draft':
            for participant in self.panel.participants.all():
                participant_data = ParticipantSerializer(instance=participant, many=False).data
                participant_available_queens = get_serialized_available_queens(self, participant)
                participants.append(
                    {'participant': participant_data, 'available_queens': participant_available_queens}
                )
        elif self.panel.status == 'wildcards':
            for participant in self.panel.participants.all():
                participant_data = ParticipantSerializer(instance=participant, many=False).data
                participant_available_queens = get_serialized_available_wq_queens(self, participant)
                participants.append(
                    {'participant': participant_data, 'available_queens': participant_available_queens}
                )
        response = {
            'participants': participants
        }
        return Response(response)


class PanelDraftApi(APIView):

    def get(self, request, *args, **kwargs):
        set_user_context(self, request, kwargs['panel_id'])
        data = get_draft_data(self)
        return Response(data)

    def put(self, request, *args, **kwargs):
        set_user_context(self, request, kwargs['panel_id'])
        request_type = request.data.get('request')
        response_status = 'ok'
        response_message = None

        has_super_perms = self.is_captain or self.is_site_admin
        has_participant_perms = has_super_perms or self.is_current_participant
        participants_actions = ['add_draft', ]

        if request_type in participants_actions and has_participant_perms:
            if request_type == 'add_draft':
                """
                {
                "request": "add_draft",
                "queen_id": 5,
                "participant_id": 1,
                "round": 1
                }
                OR to use default values
                {
                "request": "add_draft",
                "queen_id": 5,
                }
                """
                queen = Queen.objects.get(pk=request.data['queen_id'])
                participant = self.panel.current_draft_player
                if self.panel.status == 'wildcards':
                    available_queens = get_available_wq_queens(self, participant)
                else:
                    available_queens = get_available_queens(self, participant)
                if queen not in available_queens:
                    response_status = 'error'
                    response_message = '{} is not an available draft for {}'.format(queen.name, participant.name)
                else:

                    if self.panel.status == 'wildcards':
                        self.panel.save_wildcard_draft(participant, queen)
                    else:
                        self.panel.save_player_draft(participant, queen)
                    self.panel.advance_draft()

        elif has_super_perms:
            if request_type == 'end_draft':
                """
                {
                "request": "end_draft"
                }
                """
                self.panel.end_draft()
                response_message = 'Draft is ended!'

            elif request_type == 'start_draft':
                """
                {
                "request": "start_draft"
                }
                """
                self.panel.start_draft()
                response_message = 'Draft is started!'

            elif request_type == 'reset_draft':
                """
                {
                "request": "reset_draft"
                }
                """
                self.panel.reset_draft()
                response_message = 'Draft is re-set!'

        else:
            response_status = 'error'
            response_message = 'permission denied'

        response = get_draft_data(self, response_status, response_message)
        return Response(response)


class RegisterApi(APIView):
    def post(self, request, *args, **kwargs):
        request_type = request.data['request']
        if request_type == 'check-id':
            username_existing = User.objects.filter(username__iexact=request.data['username'].lower()).exists()
            email_existing = User.objects.filter(email__iexact=request.data['email'].lower()).exists()
            status = 'ok'
            errors = []
            if username_existing:
                errors.append('Username already in use')
                status = 'error'
            if email_existing:
                errors.append('Email already in use')
                status = 'error'
            response = {
                'status': status,
                'errors': errors
            }
        elif request_type == 'register':
            user = User(
                email=request.data['email'],
                username=request.data['username']
            )
            try:
                user.save()
                user.set_password(request.data['password'])
                user.save()
                response = {
                    'status': 'ok'
                }
            except:
                response = {
                    'status': 'error',
                    'message': 'Unknown internal error occurred. Please try again.'
                }
        else:
            response = {
                'status': 'error',
                'message': 'Unrecognized request.'
            }

        return Response(response)


class ProfileApi(APIView):
    def _setup(self, request):
        self.user = request.user
        self.participant = Participant.objects.get(user=self.user)

    def get(self, request, *args, **kwargs):
        self._setup(request)
        participant = UserSerializer(instance=self.participant, many=False)
        return Response(participant.data)

    def post(self, request, *args, **kwargs):
        request_type = request.data['request']
        if request_type == 'check-password':
            valid_pw = request.user.check_password(request.data['password'])
            if not valid_pw:
                response = {
                    'status': 'error',
                    'message': 'Current password is incorrect.'
                }
            else:
                response = {
                    'status': 'ok',
                    'message': None
                }
        elif request_type == 'set-password':
            try:
                request.user.set_password(request.data['password'])
                response = {
                    'status': 'ok',
                    'message': None
                }
            except Exception:
                response = {
                    'status': 'error',
                    'message': 'Could not update password. Check your input and try again.'
                }
        else:
            response = {
                'status': 'error',
                'message': 'Unrecognized request.'
            }

        return Response(response)

    def patch(self, request, *args, **kwargs):
        self._setup(request)
        field_map = {
            'email': 'email',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'display_name': 'username'
        }

        status = 'ok'
        message = None

        for patch_field, user_field in field_map.items():
            if request.data.get(patch_field):
                setattr(self.participant.user, user_field, request.data.get(patch_field))

        try:
            self.participant.user.save()
        except IntegrityError:
            status = 'error'
            message = 'That email address or username is already in use by another participant'

        participant = UserSerializer(instance=self.participant, many=False)
        return Response(
            {
                'status': status,
                'message': message,
                'participant': participant.data,

            }
        )


class CreatePanelApi(APIView):
    def get(self, request, *args, **kwargs):
        request_type = request.GET.get('request')
        status = 'ok'
        message = None
        if kwargs.get('dragrace_id'):
            drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
        else:
            panel = Panel.objects.get(pk=kwargs['panel_id'])
            drag_race = panel.drag_race

        if request_type:
            if request_type == 'checkname':
                duplicate = Panel.objects.filter(
                    name__iexact=request.GET['name'].lower(), drag_race=drag_race).exists()
                if duplicate:
                    message = 'A panel with this name already exists for {}'.format(drag_race.display_name)
            else:
                status = 'error'
                message = 'Unrecognized request'
            return Response(
                {
                    'status': status,
                    'message': message,
                    'request_type': request_type
                }
            )
        else:
            panel_data = PanelSerializer(instance=panel)
            return Response(panel_data.data)


class SiteUserApi(APIView):
    def get(self, request, *args, **kwargs):
        participant = Participant.objects.filter(user=request.user).first()
        if participant:
            site_admin = participant.site_admin
            pk = participant.pk
        else:
            site_admin = False
            pk = None

        feature_flags = FeatureFlag.objects.all()
        flags = {}
        for flag in feature_flags:
            if flag.has_users and request.user in flag.users.all():
                flags[flag.title] = flag.value == 1
            else:
                flags[flag.title] = flag.value == 1
        return Response({
            'user': {
                'is_authenticated': request.user.is_authenticated,
                'is_site_admin': site_admin,
                'pk': pk
            },
            'flags': flags
        })


class DashboardApi(APIView):
    def _serialize_dragrace(self, drag_race):
        dr_data = DragRaceSerializerMeta(instance=drag_race).data
        episodes = drag_race.episode_set.filter(is_scored=True).all()
        participant_episodes = self.participant.episodes.filter(is_scored=True, drag_race=drag_race).all()
        next_episode = drag_race.next_episode

        if next_episode:
            dr_data['next_episode'] = EpisodeSerializerShort(instance=next_episode).data
            next_episode_draft = EpisodeDraft.objects.filter(
                participant=self.participant,
                episode=next_episode
            ).first()
            dr_data['next_episode_draft'] = EpisodeDraftSerializerShort(instance=next_episode_draft).data
        else:
            dr_data['next_episode'] = None
            dr_data['next_episode_draft'] = None

        episode_draft_stats = Stats.objects.filter(
            participant=self.participant,
            drag_race=drag_race,
            stat_type='cummulative_dragrace_drafts').first()
        if episode_draft_stats:
            dr_data['episode_drafts'] = StatSerializer(instance=episode_draft_stats).data

            rank_stats = Stats.objects.filter(
                participant=self.participant,
                drag_race=drag_race,
                stat_type='dragrace_rank').first()
            dr_data['general_rank'] = StatSerializer(instance=rank_stats).data
        else:
            dr_data['episode_drafts'] = None
            dr_data['general_rank'] = None

        dr_data['episodes'] = []

        for episode in episodes:
            ep_data = EpisodeSerializerShort(instance=episode).data
            if episode in participant_episodes:
                ep_data['is_viewed'] = True
            else:
                ep_data['is_viewed'] = False
            dr_data['episodes'].append(ep_data)

        dr_data['panels'] = []
        panels = self.participant.panel_set.filter(drag_race=drag_race).all()
        for _panel in panels:
            panel_scores = StatSerializer(
                instance=Stats.objects.filter(
                    stat_type='dragrace_panel_scores',
                    participant=self.participant,
                    drag_race=drag_race,
                    panel=_panel
                ).first()
            ).data
            panel_data = PanelSerializerMeta(instance=_panel).data
            for _p in panel_data['participants']:
                _p['scores'] = {}
                pk = _p['pk']
                if panel_scores.get('data'):
                    for pscore in panel_scores['data']:
                        if pscore['participant']['pk'] == pk:
                            _p['scores'] = pscore['score']
            dr_data['panels'].append(panel_data)
        return dr_data

    def get(self, request, *args, **kwargs):
        setcontext(self, request)
        if kwargs.get('dragrace_id'):
            drag_race = DragRace.objects.get(pk=kwargs.get('dragrace_id'))
        else:
            drag_race = None
        request_type = request.GET.get('request')

        if not drag_race:
            if request_type == 'old-seasons':
                self.response.update({'drag_races': []})
                past_races = DragRace.objects.filter(is_current=False).exclude(
                    status='pending').order_by('-season').all()
                for drag_race in past_races:
                    dr_data = self._serialize_dragrace(drag_race)
                    self.response['drag_races'].append(dr_data)

            else:
                self.response.update({'drag_races': []})
                current_races = DragRace.objects.filter(
                    is_current=True).exclude(status='pending').order_by('-season').all()

                for drag_race in current_races:
                    dr_data = self._serialize_dragrace(drag_race)
                    self.response['drag_races'].append(dr_data)
        else:
            self.response['drag_race'] = self._serialize_dragrace(drag_race)
        return Response(self.response)

    def post(self, request, *args, **kwargs):
        setcontext(self, request)
        request_type = request.data['request']
        if request_type == 'ruveal-episode':
            episode = Episode.objects.get(pk=request.data['episode_id'])
            self.participant.episodes.add(episode)
            self.participant.save()
            refresh_dragrace_stats_for_participant(self.participant, episode.drag_race)
            self.response['drag_race'] = self._serialize_dragrace(episode.drag_race)
            return Response(self.response)
