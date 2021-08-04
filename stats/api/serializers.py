from rest_framework import serializers
from stats.models import (
    EpisodeDraftScore,
    DragRaceDraftScore,
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
)

from fantasydrag.api.serializers import (
    QueenSerializer,
    EpisodeSerializerShort,
    ParticipantSerializer,
)


class DragRaceDraftScoreSerializer(serializers.HyperlinkedModelSerializer):
    participant = ParticipantSerializer()

    class Meta:
        model = DragRaceDraftScore
        fields = [
            'participant',
            'total_score',
            'rank_tier',
            'total_participants'
        ]


class EpisodeDraftScoreSerializer(serializers.HyperlinkedModelSerializer):
    drafted_queens = QueenSerializer(many=True)

    class Meta:
        model = EpisodeDraftScore
        fields = [
            'total_score',
            'rank_tier',
            'total_participants',
            'drafted_queens'
        ]


class QueenEpisodeSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerializer()
    # episode_scores = ScoreSerializer(many=True)
    episode = EpisodeSerializerShort()

    class Meta:
        model = QueenEpisodeScore
        fields = [
            'queen',
            'episode',
            'total_score',
        ]


class QueenEpisodeScoreSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerializer()

    class Meta:
        model = QueenEpisodeScore
        fields = [
            'queen',
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
