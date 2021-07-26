from rest_framework import serializers
from stats.models import (
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
)

from fantasydrag.api.serializers import (
    QueenSerializer,
    ScoreSerializer,
    EpisodeSerializerShort,
    DragRaceSerializerMeta,
    ParticipantSerializer,
    PanelSerializerMeta,
)


class QueenEpisodeSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerializer()
    episode_scores = ScoreSerializer(many=True)
    episode = EpisodeSerializerShort()

    class Meta:
        model = QueenEpisodeScore
        fields = [
            'queen',
            'episode',
            'total_score',
            'episode_scores'
        ]


class QueenDragRaceSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerializer()
    scores = QueenEpisodeSerializer(many=True)

    class Meta:
        model = QueenDragRaceScore
        fields = [
            'queen',
            'total_score',
            'scores'
        ]


class PanelEpisodeSerializer(serializers.HyperlinkedModelSerializer):
    panelist = ParticipantSerializer()
    scores = QueenEpisodeSerializer(many=True)

    class Meta:
        model = PanelistEpisodeScore
        fields = [
            'panelist',
            'total_score',
            'scores',
        ]


class PanelDragRaceSerializer(serializers.HyperlinkedModelSerializer):
    panelist = ParticipantSerializer()

    class Meta:
        model = PanelistDragRaceScore
        fields = [
            'panelist',
            'total_score'
        ]
