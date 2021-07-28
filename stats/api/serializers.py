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
    ParticipantSerializer,
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
        ]


class QueenDragRaceSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerializer()

    class Meta:
        model = QueenDragRaceScore
        fields = [
            'queen',
            'total_score',
        ]


class PanelistEpisodeSerializer(serializers.HyperlinkedModelSerializer):
    panelist = ParticipantSerializer()

    class Meta:
        model = PanelistEpisodeScore
        fields = [
            'panelist',
            'total_score',
        ]


class PanelistDragRaceSerializer(serializers.HyperlinkedModelSerializer):
    panelist = ParticipantSerializer()

    class Meta:
        model = PanelistDragRaceScore
        fields = [
            'panelist',
            'total_score'
        ]
