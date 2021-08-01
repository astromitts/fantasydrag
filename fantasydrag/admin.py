from django.contrib import admin
from django import forms
from fantasydrag.models import (
    DragRace,
    Episode,
    EpisodeDraft,
    Queen,
    DefaultRule,
    Score,
    Participant,
    Panel,
    Draft,
    WildCardQueen,
    WildCardAppearance,
    AppearanceType,
)

from fantasydrag.stats import Stats


class FormBase(forms.ModelForm):
    fields = '__all__'


class DragRaceAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['display_name', 'drag_race_type', 'franchise', 'season', 'status', 'is_current']
    list_editable = ['drag_race_type', 'franchise', 'is_current', 'status']


class QueenAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['name', 'normalized_name', 'main_franchise', 'tier_score', 'total_score']
    list_filter = ['main_franchise']


class EpisodeAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['number', 'title', 'has_aired', 'is_scored', 'drag_race']
    list_editable = ['title', 'has_aired', ]
    list_filter = ['drag_race', ]


class DefaultRuleAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['name', 'score_type', 'point_value', 'score_class']
    list_editable = ['score_type', 'point_value', 'score_class']
    list_filter = ['score_type', 'drag_race_types']


class ScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['pk', 'queen', 'default_rule', 'episode']
    list_filter = ['default_rule', 'episode__drag_race']


class ParticipantAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['display_name', 'user']


class StatsAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['stat_type', 'participant', 'drag_race', 'queen', 'panel']
    list_filter = ['stat_type', 'participant', 'drag_race', 'queen', 'panel']


class PanelAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['name', 'drag_race', 'panel_type', 'status']
    readonly_fields = ['draft_rounds', 'draft_order', 'total_drafts', 'participant_drafts']


class DraftAdmin(admin.ModelAdmin):
    form = FormBase


class WildCardQueenAdmin(admin.ModelAdmin):
    form = FormBase


class WildCardAppearanceAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['queen', 'episode']


class AppearanceTypeAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['name', 'point_value', 'description']


class EpisodeDraftAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['participant', 'episode', 'score']


admin.site.register(EpisodeDraft, EpisodeDraftAdmin)
admin.site.register(DragRace, DragRaceAdmin)
admin.site.register(Queen, QueenAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(DefaultRule, DefaultRuleAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Stats, StatsAdmin)
admin.site.register(Panel, PanelAdmin)
admin.site.register(Draft, DraftAdmin)
admin.site.register(WildCardQueen, WildCardQueenAdmin)
admin.site.register(WildCardAppearance, WildCardAppearanceAdmin)
admin.site.register(AppearanceType, AppearanceTypeAdmin)
