from rest_framework.response import Response
from rest_framework.views import APIView

from fantasydrag.models import (
    Episode,
    Draft,
    Rule,
    Score,
    Queen,
    Panel,
    Participant,
)
from fantasydrag.api.serializers import (
    DraftSerializer,
    EpisodeScore,
    ScoreSerializer,
    PanelSerializer,
    QueenSerializer,
    ParticipantSerializer,
)


def get_available_queens(view, participant):
    participant_drafts = view.panel.draft_set.filter(participant=participant)
    drafted_queens = [pd.queen for pd in participant_drafts]

    queens_by_draft_count = {}
    for draft in view.panel.draft_set.all():
        this_count = queens_by_draft_count.get(draft.queen, 0)
        this_count += 1
        queens_by_draft_count[draft.queen] = this_count

    available_queens = []
    if view.panel.draft_type == 'byQueenCount':
        for queen in view.panel.drag_race.queens.all():
            if queens_by_draft_count.get(queen, 0) < view.panel.queen_draft_allowance and queen not in drafted_queens:  # noqa
                available_queens.append(queen)
    else:
        for queen in view.panel.drag_race.queens.all():
            this_count = queens_by_draft_count.get(queen, 0)
            if this_count < view.panel.draft_data['max_queen_draft'] and queen not in drafted_queens:
                available_queens.append(queen)

    return available_queens


def get_serialized_available_queens(view, participant):
    available_queens = get_available_queens(view, participant)
    available_queens_serialized = QueenSerializer(instance=available_queens, many=True)
    available_queens_data = available_queens_serialized.data
    return available_queens_data


def set_user_context(view, request, panel_id):
    view.panel = Panel.objects.get(pk=panel_id)
    view.user = request.user
    view.request_participant = Participant.objects.get(user=view.user)
    view.is_site_admin = view.request_participant.site_admin
    view.is_captain = view.request_participant in view.panel.captains.all()
    view.is_current_participant = view.request_participant == view.panel.current_draft_player


class EpisodeApi(APIView):
    def get(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        serializer = EpisodeScore(instance=episode, many=False)
        response = serializer.data
        return Response(response)

    def put(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        queen = Queen.objects.get(pk=request.data['queen'])
        rule = Rule.objects.get(pk=request.data['rule'])
        score = Score(
            episode=episode,
            rule=rule,
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
            'panel': {
                'status': self.panel.status
            }
        }
        return Response(response)


class DraftAvailableQueensApi(APIView):
    def get(self, request, *args, **kwargs):
        set_user_context(self, request, kwargs['panel_id'])
        participants = []
        for participant in self.panel.participants.all():
            participant_data = ParticipantSerializer(instance=participant, many=False).data
            participant_available_queens = get_serialized_available_queens(self, participant)
            participants.append(
                {'participant': participant_data, 'available_queens': participant_available_queens}
            )
        response = {
            'participants': participants
        }
        return Response(response)


class PanelDraftApi(APIView):

    def _get_draft_data(self, response_status='ok', response_message=None):
        panel_data = PanelSerializer(instance=self.panel, many=False).data
        participants = []
        if self.panel.draft_data['participant_order']:
            for participant_order in self.panel.draft_data['participant_order']:
                participant = self.panel.participants.get(pk=participant_order)
                participant_data = ParticipantSerializer(instance=participant, many=False).data
                participant_available_queens = get_serialized_available_queens(self, participant)
                participants.append(
                    {'participant': participant_data, 'available_queens': participant_available_queens}
                )
        else:
            for participant in self.panel.participants.all():
                participant_data = ParticipantSerializer(instance=participant, many=False).data
                participant_available_queens = get_serialized_available_queens(self, participant)
                participants.append(
                    {'participant': participant_data, 'available_queens': participant_available_queens}
                )

        panel_drafts = Draft.objects.filter(panel=self.panel).order_by('-round_selected', '-pk').all()
        drafts_data = DraftSerializer(instance=panel_drafts, many=True).data
        request_status = {
            'status': response_status,
            'message': response_message,
            'is_site_admin': self.is_site_admin,
            'is_captain': self.is_captain,
            'is_current_participant': self.is_current_participant,
            'request_participant': self.request_participant.pk,
        }
        return {
            'meta': request_status,
            'panel': panel_data,
            'participants': participants,
            'drafts': drafts_data,
        }

    def get(self, request, *args, **kwargs):
        set_user_context(self, request, kwargs['panel_id'])
        data = self._get_draft_data()
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
                participant = Participant.objects.get(
                    pk=request.data.get('participant_id', self.panel.draft_data['current_participant'])
                )
                available_queens = get_available_queens(self, participant)
                if queen not in available_queens:
                    response_status = 'error'
                    response_message = '{} is not an available draft for {}'.format(queen.name, participant.name)
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
                self.panel.start_draft(
                    draft_type=request.data['draft_type'],
                    variable_number=request.data['variable_number'],
                    draft_rule_set=request.data['draft_rules']
                )
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

        response = self._get_draft_data(response_status, response_message)
        return Response(response)
