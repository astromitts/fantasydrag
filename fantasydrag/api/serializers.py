from rest_framework import serializers

from fantasydrag.models import (
    AppearanceType,
    DragRace,
    DragRaceType,
    Draft,
    Episode,
    DefaultRule,
    Score,
    Queen,
    Panel,
    Participant,
    WildCardAppearance,
    WildCardQueen,
)


class DragRaceTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DragRaceType
        fields = [
            'name',
        ]


class AppearanceTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AppearanceType
        fields = [
            'pk',
            'name',
            'point_value',
            'description',
        ]


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
        model = DefaultRule
        fields = [
            'pk',
            'name',
            'description',
            'point_value',
            'score_type',
            'drag_race_types_list'
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
            'drag_race_type_name',
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


class EpisodeSerializer(serializers.HyperlinkedModelSerializer):
    drag_race = DragRaceSerializerShort()

    class Meta:
        model = Episode
        fields = [
            'pk',
            'drag_race',
            'number',
            'title',
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


class WQDraftSerializer(serializers.HyperlinkedModelSerializer):
    participant = ParticipantSerializer(many=False)
    queen = QueenSerializer(many=False)

    class Meta:
        model = WildCardQueen
        fields = ['pk', 'participant', 'queen']


class PanelSerializer(serializers.HyperlinkedModelSerializer):
    drag_race = DragRaceSerializer(many=False)

    class Meta:
        model = Panel
        fields = [
            'pk',
            'name',
            'status',
            'participant_limit',
            'panel_type',
            'draft_order',
            'draft_rounds',
            'participant_drafts',
            'current_round',
            'wildcard_allowance',
            'current_participant',
            'drag_race',
        ]


class AppearanceSerializer(serializers.HyperlinkedModelSerializer):
    queen = QueenSerializer()
    appearance = AppearanceTypeSerializer()
    episode = EpisodeSerializer()

    class Meta:
        model = WildCardAppearance
        fields = [
            'pk',
            'queen',
            'episode',
            'appearance',
        ]


class QueenSearchSerializer(serializers.HyperlinkedModelSerializer):
    drag_races = DragRaceSerializerShort(many=True, source='dragrace_set')

    class Meta:
        model = Queen
        fields = [
            'pk',
            'name',
            'main_franchise',
            'drag_races'
        ]
