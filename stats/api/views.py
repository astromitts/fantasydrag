from rest_framework.response import Response
from rest_framework.views import APIView

from fantasydrag.models import (
    DragRace,
    Queen,
    Episode,
    Panel,
    Participant
)
from fantasydrag.api.serializers import (
    PanelSerializerMeta,
)

from stats.models import (
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
)

from stats.api.serializers import (
    QueenDragRaceSerializer,
    QueenEpisodeSerializer,
    PanelEpisodeSerializer,
    PanelDragRaceSerializer,
    DragRaceSerializerMeta,
    EpisodeSerializerShort
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
            result = PanelEpisodeSerializer(instance=instance).data
        else:
            instance = PanelistEpisodeScore.objects.filter(
                viewing_participant=self.viewing_participant,
                episode=self.episode
            ).all()
            result = PanelEpisodeSerializer(instance=instance, many=True).data
        return Response(result)


class DragRacePanelApiView(StatApiView):
    def get(self, request, *args, **kwargs):
        self.set_context(request, *args, **kwargs)
        panelist_instance = PanelistDragRaceScore.objects.filter(
            panel=self.panel,
            viewing_participant=self.viewing_participant
        ).all()
        panelist_data = PanelDragRaceSerializer(instance=panelist_instance, many=True).data
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
        current_drag_races = DragRace.objects.filter(status='active')
        result = {'drag_races': []}
        viewed_episodes = self.viewing_participant.episodes.all()
        viewed_episode_pks = [ve.pk for ve in viewed_episodes]
        for drag_race in current_drag_races:
            panels = self.viewing_participant.panel_set.filter(drag_race=drag_race)
            dragrace_data = DragRaceSerializerMeta(instance=drag_race).data
            episodes = EpisodeSerializerShort(
                instance=drag_race.episode_set.filter(has_aired=True).all(), many=True).data
            for episode in episodes:
                episode['is_viewed'] = episode['pk'] in viewed_episode_pks
            dragrace_data['episodes'] = episodes
            dragrace_data['panels'] = []
            for panel in panels:
                panel_data = PanelSerializerMeta(instance=panel).data
                panelist_instances = PanelistDragRaceScore.objects.filter(
                    panel=panel,
                    viewing_participant=self.viewing_participant
                ).order_by('-total_score').all()
                panelist_data = PanelDragRaceSerializer(instance=panelist_instances, many=True).data
                panel_data['panelists'] = panelist_data
                dragrace_data['panels'].append(panel_data)

            queen_instance = QueenDragRaceScore.objects.filter(
                viewing_participant=self.viewing_participant,
                drag_race=drag_race,
            ).order_by('-total_score').all()
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
