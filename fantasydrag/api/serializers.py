from rest_framework import serializers

from fantasydrag.models import (
    Episode,
    Rule,
    Score,
    Queen
)


class QueenSerlaizer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Queen
        fields = [
            'pk',
            'name'
        ]


class RuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rule
        fields = [
            'pk',
            'name',
            'description',
            'point_value'
        ]


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerlaizer(many=False)
    rule = RuleSerializer(many=False)

    class Meta:
        model = Score
        fields = [
            'pk',
            'queen',
            'rule',
        ]


class EpisodeScore(serializers.HyperlinkedModelSerializer):
    rules = RuleSerializer(source='drag_race.rule_set', many=True)
    scores = ScoreSerializer(source='score_set', many=True)
    queens = QueenSerlaizer(source='drag_race.queens', many=True)

    class Meta:
        model = Episode
        fields = [
            'pk',
            'number',
            'title',
            'is_scored',
            'queens',
            'scores',
            'rules'
        ]
