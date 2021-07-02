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


class PanelDraftApi(APIView):
    def _set_user_context(self, request, panel_id):
        self.panel = Panel.objects.get(pk=panel_id)
        self.user = request.user
        self.request_participant = Participant.objects.get(user=self.user)
        self.is_site_admin = self.request_participant.site_admin
        self.is_captain = self.request_participant in self.panel.captains.all()
        self.is_current_participant = self.request_participant == self.panel.current_draft_player

    def _get_available_queens(self, participant):
        participant_drafts = self.panel.draft_set.filter(participant=participant)
        drafted_queens = [pd.queen for pd in participant_drafts]

        queens_by_draft_count = {}
        for draft in self.panel.draft_set.all():
            this_count = queens_by_draft_count.get(draft.queen, 0)
            this_count += 1
            queens_by_draft_count[draft.queen] = this_count

        available_queens = []
        if self.panel.draft_type == 'byQueenCount':
            for queen in self.panel.drag_race.queens.all():
                if queens_by_draft_count.get(queen, 0) < self.panel.queen_draft_allowance and queen not in drafted_queens:  # noqa
                    available_queens.append(queen)
        else:
            for queen in self.panel.drag_race.queens.all():
                this_count = queens_by_draft_count.get(queen, 0)
                if this_count < self.panel.draft_data['max_queen_draft'] and queen not in drafted_queens:
                    available_queens.append(queen)

        return available_queens

    def _get_serialized_available_queens(self, participant):
        available_queens = self._get_available_queens(participant)
        available_queens_serialized = QueenSerializer(instance=available_queens, many=True)
        available_queens_data = available_queens_serialized.data
        return available_queens_data

    def _get_draft_data(self, response_status='ok', response_message=None):
        panel_data = PanelSerializer(instance=self.panel, many=False).data
        participants = []
        if self.panel.draft_data['participant_order']:
            for participant_order in self.panel.draft_data['participant_order']:
                participant = self.panel.participants.get(pk=participant_order)
                participant_data = ParticipantSerializer(instance=participant, many=False).data
                participant_available_queens = self._get_serialized_available_queens(participant)
                participants.append(
                    {'participant': participant_data, 'available_queens': participant_available_queens}
                )
        else:
            for participant in self.panel.participants.all():
                participant_data = ParticipantSerializer(instance=participant, many=False).data
                participant_available_queens = self._get_serialized_available_queens(participant)
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
        }
        return {
            'meta': request_status,
            'panel': panel_data,
            'participants': participants,
            'drafts': drafts_data,
        }

    def get(self, request, *args, **kwargs):
        self._set_user_context(request, kwargs['panel_id'])
        data = self._get_draft_data()
        return Response(data)

    def put(self, request, *args, **kwargs):
        self._set_user_context(request, kwargs['panel_id'])
        if self.is_captain or self.is_site_admin:
            request_type = request.data.get('request')
            response_status = 'ok'
            response_message = None
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
                available_queens = self._get_available_queens(participant)
                if queen not in available_queens:
                    response_status = 'error'
                    response_message = '{} is not an available draft for {}'.format(queen.name, participant.name)
                else:
                    self.panel.save_player_draft(participant, queen)
                    self.panel.advance_draft()
            elif request_type == 'end_draft':
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
