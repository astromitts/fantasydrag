from rest_framework import serializers

from fantasydrag.models import (
    AppearanceType,
    DragRace,
    DragRaceType,
    Draft,
    DefaultRule,
    Episode,
    EpisodeDraft,
    Panel,
    Participant,
    Queen,
    Score,
    WildCardAppearance,
    WildCardQueen,
)
from fantasydrag.stats import Stats


class StatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stats
        fields = [
            'data',
            'primary_stat_display'
        ]


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
            'general_draft_allowance',
            'queens',
            'rules'
        ]


class DragRaceSerializerMeta(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DragRace
        fields = [
            'pk',
            'display_name',
            'status',
            'season',
            'franchise',
            'drag_race_type_name',
            'rules_url',
            'detail_url',
            'edit_url',
            'new_panel_url',
            'public_panels_url',
        ]


class EpisodeSerializer(serializers.HyperlinkedModelSerializer):
    drag_race = DragRaceSerializerMeta()

    class Meta:
        model = Episode
        fields = [
            'pk',
            'drag_race',
            'number',
            'title',
            'has_aired',
            'is_scored'
        ]


class EpisodeSerializerShort(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Episode
        fields = [
            'pk',
            'number',
            'title',
            'has_aired',
            'is_scored',
            'edit_draft_url',
            'detail_url'
        ]


class EpisodeDraftSerializer(serializers.HyperlinkedModelSerializer):
    episode = EpisodeSerializer()
    queens = QueenSerializer(many=True, source='episode.drag_race.queens')
    selected_queens = QueenSerializer(many=True, source='queens')

    class Meta:
        model = EpisodeDraft
        fields = [
            'pk',
            'episode',
            'queens',
            'selected_queens',
        ]


class EpisodeDraftSerializerShort(serializers.HyperlinkedModelSerializer):
    selected_queens = QueenSerializer(many=True, source='queens')

    class Meta:
        model = EpisodeDraft
        fields = [
            'pk',
            'selected_queens',
            'score',
            'rank_tier',
            'total_participants'
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
            'has_aired',
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


class PanelSerializerMetaShort(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Panel
        fields = [
            'pk',
            'name',
            'status',
            'detail_url',
            'draft_url',
        ]


class PanelSerializerMeta(serializers.HyperlinkedModelSerializer):
    participants = ParticipantSerializer(many=True)

    class Meta:
        model = Panel
        fields = [
            'pk',
            'name',
            'status',
            'detail_url',
            'draft_url',
            'participants',
        ]


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
    drag_races = DragRaceSerializerMeta(many=True, source='dragrace_set')

    class Meta:
        model = Queen
        fields = [
            'pk',
            'name',
            'main_franchise',
            'drag_races'
        ]
