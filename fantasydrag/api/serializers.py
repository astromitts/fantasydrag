from rest_framework import serializers

from fantasydrag.models import (
    DragRace,
    Draft,
    Episode,
    Rule,
    Score,
    Queen,
    Panel,
    Participant,
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Participant
        fields = [
            'pk',
            'display_name',
            'first_name',
            'last_name',
            'email',
        ]


class QueenSerializer(serializers.HyperlinkedModelSerializer):
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


class DragRaceSerializer(serializers.HyperlinkedModelSerializer):
    queens = QueenSerializer(many=True)
    rules = RuleSerializer(many=True, source='rule_set')

    class Meta:
        model = DragRace
        fields = [
            'pk',
            'display_name',
            'season',
            'franchise',
            'race_type',
            'queens',
            'rules'
        ]


class DragRaceSerializerShort(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DragRace
        fields = [
            'pk',
            'display_name',
        ]


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerializer(many=False)
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
    queens = QueenSerializer(source='drag_race.queens', many=True)

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


class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Participant
        fields = ['pk', 'name']


class DraftSerializer(serializers.HyperlinkedModelSerializer):
    participant = ParticipantSerializer(many=False)
    queen = QueenSerializer(many=False)

    class Meta:
        model = Draft
        fields = ['pk', 'participant', 'queen', 'round_selected']


class PanelSerializer(serializers.HyperlinkedModelSerializer):
    drag_race = DragRaceSerializer(many=False)

    class Meta:
        model = Panel
        fields = [
            'pk',
            'name',
            'status',
            'draft_type',
            'draft_data',
            'queen_draft_allowance',
            'team_size',
            'drag_race',
        ]
