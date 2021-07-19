from django.contrib import admin
from django import forms
from fantasydrag.models import (
    DragRace,
    Episode,
    Queen,
    DefaultRule,
    Score,
    Participant,
    Stats,
    Panel,
    Draft,
    WildCardQueen,
    WildCardAppearance,
    AppearanceType,
)


class FormBase(forms.ModelForm):
    fields = '__all__'


class DragRaceForm(FormBase):
    pass


class QueenForm(FormBase):
    pass


class EpisodeForm(FormBase):
    pass


class DefaultRuleForm(FormBase):
    pass


class ScoreForm(FormBase):
    pass


class ParticipantForm(FormBase):
    pass


class StatsForm(FormBase):
    pass


class PanelForm(FormBase):
    pass


class DraftForm(FormBase):
    pass


class WildCardQueenForm(FormBase):
    pass


class WildCardAppearanceForm(FormBase):
    pass


class AppearanceTypeForm(FormBase):
    pass


class DragRaceAdmin(admin.ModelAdmin):
    form = DragRaceForm
    list_display = ['display_name', 'drag_race_type', 'franchise', 'season', 'status', 'is_current']
    list_editable = ['drag_race_type', 'franchise', 'is_current', 'status']


class QueenAdmin(admin.ModelAdmin):
    form = QueenForm
    list_display = ['name', 'normalized_name', 'main_franchise', 'tier_score', 'total_score']
    list_filter = ['main_franchise']


class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeForm
    list_display = ['number', 'title', 'has_aired', 'is_scored', 'drag_race']
    list_editable = ['title', 'has_aired', ]
    list_filter = ['drag_race', ]


class DefaultRuleAdmin(admin.ModelAdmin):
    form = DefaultRuleForm
    list_display = ['name', 'score_type', 'point_value', 'description']
    list_editable = ['score_type', 'point_value', 'description']
    list_filter = ['score_type', 'drag_race_types']


class ScoreAdmin(admin.ModelAdmin):
    form = ScoreForm
    list_display = ['pk', 'queen', 'default_rule', 'episode']
    list_filter = ['default_rule', 'episode__drag_race']


class ParticipantAdmin(admin.ModelAdmin):
    form = ParticipantForm
    list_display = ['display_name', 'user']


class StatsAdmin(admin.ModelAdmin):
    form = StatsForm
    list_display = ['stat_type', 'participant', 'drag_race', 'queen', 'panel']
    list_filter = ['stat_type', 'participant', 'drag_race', 'queen', 'panel']


class PanelAdmin(admin.ModelAdmin):
    form = PanelForm
    list_display = ['name', 'drag_race', 'panel_type', 'status']
    readonly_fields = ['draft_rounds', 'draft_order', 'total_drafts', 'participant_drafts']


class DraftAdmin(admin.ModelAdmin):
    form = PanelForm


class WildCardQueenAdmin(admin.ModelAdmin):
    form = WildCardQueenForm


class WildCardAppearanceAdmin(admin.ModelAdmin):
    form = WildCardAppearanceForm
    list_display = ['queen', 'episode']


class AppearanceTypeAdmin(admin.ModelAdmin):
    form = AppearanceTypeForm
    list_display = ['name', 'point_value', 'description']


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
