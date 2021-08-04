from rest_framework.response import Response
from rest_framework.views import APIView

from flags.models import FeatureFlag
from fantasydrag.models import (
    DragRace,
    Episode,
    EpisodeDraft,
    Panel,
    Participant,
    Queen,
)
from fantasydrag.api.serializers import (
    DragRaceSerializerMeta,
    EpisodeSerializerShort,
    EpisodeDraftSerializerShort,
    PanelSerializerMetaShort,
)

from stats.models import (
    CanonicalQueenDragRaceScore,
    EpisodeDraftScore,
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
)

from stats.api.serializers import (
    EpisodeDraftScoreSerializer,
    QueenDragRaceSerializer,
    QueenEpisodeSerializer,
    QueenEpisodeScoreSerializer,
    PanelistEpisodeSerializer,
    PanelistDragRaceSerializer,
)

from stats.utils import set_viewing_participant_scores


class StatApiView(APIView):
    def set_context(self, request, *args, **kwargs):
        self.viewing_participant = request.user.participant
        if 'dragrace_id' in kwargs:
            self.drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
        if 'episode_id' in kwargs:
            self.episode = Episode.objects.get(pk=kwargs['episode_id'])
            self.drag_race = self.episode.drag_race
        if 'queen_id' in self.kwargs:
            self.queen = Queen.objects.get(pk=kwargs['queen_id'])
        if 'panel_id' in self.kwargs:
            self.panel = Panel.objects.get(pk=kwargs['panel_id'])
            self.drag_race = self.panel.drag_race
        if 'target_participant_id' in self.kwargs:
            self.target_participant = Participant.objects.get(pk=kwargs['target_participant_id'])
        else:
            self.target_participant = None


class EpisodeQueenApiView(StatApiView):
    def get(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        instance = QueenEpisodeScore.objects.get(
            viewing_participant=self.viewing_participant,
            episode=self.episode,
            queen=self.queen
        )
        result = QueenEpisodeSerializer(instance=instance).data
        return Response(result)


class DragRaceQueenApiView(StatApiView):
    def get(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        instance = QueenDragRaceScore.objects.get(
            viewing_participant=self.viewing_participant,
            drag_race=self.drag_race,
            queen=self.queen
        )
        result = QueenDragRaceSerializer(instance=instance).data
        return Response(result)


class EpisodePanelApiView(StatApiView):
    def get(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        if self.target_participant:
            instance = PanelistEpisodeScore.objects.get(
                viewing_participant=self.viewing_participant,
                episode=self.episode,
                panelist=self.target_participant
            )
            result = PanelistEpisodeSerializer(instance=instance).data
        else:
            instance = PanelistEpisodeScore.objects.filter(
                viewing_participant=self.viewing_participant,
                episode=self.episode
            ).all()
            result = PanelistEpisodeSerializer(instance=instance, many=True).data
        return Response(result)


class DragRacePanelApiView(StatApiView):
    def get(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        panelist_instance = PanelistDragRaceScore.objects.filter(
            panel=self.panel,
            viewing_participant=self.viewing_participant
        ).all()
        panelist_data = PanelistDragRaceSerializer(instance=panelist_instance, many=True).data
        queen_instance = QueenDragRaceScore.objects.filter(
            viewing_participant=self.viewing_participant,
            drag_race=self.drag_race,
        ).all()
        queen_data = QueenDragRaceSerializer(instance=queen_instance, many=True).data
        return Response({
            'panel': panelist_data,
            'queens': queen_data
        })


class StatsDashboardApiView(StatApiView):
    def get(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        if 'dragrace_id' in kwargs:
            drag_races = [DragRace.objects.get(pk=kwargs['dragrace_id']), ]
        elif 'dragrace_status' in kwargs:
            if kwargs['dragrace_status'] == 'admin':
                drag_races = DragRace.objects.exclude(status='active')
            else:
                drag_races = DragRace.objects.filter(status=kwargs['dragrace_status'])
        else:
            drag_races = DragRace.objects.filter(status='active')
        result = {'drag_races': []}
        viewed_episodes = self.viewing_participant.episodes.all()
        for drag_race in drag_races:
            if drag_race.status == 'active':
                queen_qs = QueenDragRaceScore.objects.filter(
                    viewing_participant=self.viewing_participant,
                    drag_race=drag_race,
                )
            else:
                queen_qs = CanonicalQueenDragRaceScore.objects.filter(
                    drag_race=drag_race,
                )

            panels = self.viewing_participant.panel_set.filter(drag_race=drag_race)
            dragrace_data = DragRaceSerializerMeta(instance=drag_race).data

            scored_episodes = drag_race.episode_set.filter(is_scored=True).all()
            next_episode = drag_race.episode_set.filter(is_scored=False).first()

            if next_episode:
                episodes_to_display = [episode for episode in scored_episodes] + [next_episode, ]
            else:
                episodes_to_display = scored_episodes

            episodes = []
            for episode in episodes_to_display:
                episode_data = EpisodeSerializerShort(instance=episode).data

                if FeatureFlag.flag_is_true('GENERAL_DRAFT', request.user):
                    if episode.is_scored:
                        episode_draft = EpisodeDraftScore.objects.filter(
                            participant=self.viewing_participant, episodedraft__episode=episode).first()
                        episode_data['draft'] = EpisodeDraftScoreSerializer(instance=episode_draft).data
                    else:
                        episode_draft = EpisodeDraft.objects.filter(
                            participant=self.viewing_participant, episode=episode).first()
                        episode_data['draft'] = EpisodeDraftSerializerShort(instance=episode_draft).data

                episode_data['is_viewed'] = episode in viewed_episodes
                episode_queen_scores = QueenEpisodeScore.objects.filter(
                    viewing_participant=self.viewing_participant,
                    episode=episode
                ).order_by('-total_score').all()
                queen_scores_data = QueenEpisodeScoreSerializer(instance=episode_queen_scores, many=True).data
                queens = {}
                for queen_score in queen_scores_data:
                    queens[queen_score['queen']['pk']] = {
                        'pk': queen_score['queen']['pk'],
                        'name': queen_score['queen']['name'],
                        'score': queen_score['total_score']
                    }
                episode_data['queens'] = queens
                episodes.append(episode_data)
            dragrace_data['episodes'] = episodes
            dragrace_data['panels'] = []
            for panel in panels:
                panel_data = PanelSerializerMetaShort(instance=panel).data
                panelist_instances = PanelistDragRaceScore.objects.filter(
                    panel=panel,
                    viewing_participant=self.viewing_participant
                ).order_by('-total_score').all()
                panelist_data = PanelistDragRaceSerializer(instance=panelist_instances, many=True).data
                panel_data['panelists'] = panelist_data
                dragrace_data['panels'].append(panel_data)

            queen_instance = queen_qs.order_by('-total_score').all()
            queen_data = QueenDragRaceSerializer(instance=queen_instance, many=True).data
            dragrace_data['queens'] = queen_data
            result['drag_races'].append(dragrace_data)

        return Response(result)

    def post(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        request_type = request.data['request']
        if request_type == 'ruveal-episode':
            episode = Episode.objects.get(pk=request.data['episode_id'])
            self.viewing_participant.episodes.add(episode)
            self.viewing_participant.save()
            set_viewing_participant_scores(self.viewing_participant, episode.drag_race)
            return Response({})
        if request_type == 'hide-episode':
            episode = Episode.objects.get(pk=request.data['episode_id'])
            self.viewing_participant.episodes.remove(episode)
            self.viewing_participant.save()
            set_viewing_participant_scores(self.viewing_participant, episode.drag_race)
            return Response({})


class StatsEpisodeScoreApiView(StatApiView):
    def post(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        endpoint = kwargs['endpoint']
        if endpoint == 'reset-scores':
            for participant in Participant.objects.all():
                set_viewing_participant_scores(participant, self.episode.drag_race)
        return Response({})
