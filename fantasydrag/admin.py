from django.contrib import admin
from django import forms
from fantasydrag.models import (
    DragRace,
    Episode,
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
    list_display = ['display_name', 'drag_race_type', 'season']
    list_editable = ['drag_race_type']


class QueenAdmin(admin.ModelAdmin):
    form = QueenForm
    list_display = ['name', 'normalized_name', 'main_franchise', 'tier_score', 'total_score']
    list_filter = ['main_franchise']


class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeForm
    list_display = ['number', 'title', 'drag_race']
    list_editable = ['title', ]


class DefaultRuleAdmin(admin.ModelAdmin):
    form = DefaultRuleForm
    list_display = ['name', 'score_type', 'point_value', 'drag_race_type', 'description']
    list_editable = ['score_type', 'point_value', 'drag_race_type', 'description']
    list_filter = ['score_type', 'drag_race_type']


class ScoreAdmin(admin.ModelAdmin):
    form = ScoreForm


class ParticipantAdmin(admin.ModelAdmin):
    form = ParticipantForm


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
admin.site.register(Panel, PanelAdmin)
admin.site.register(Draft, DraftAdmin)
admin.site.register(WildCardQueen, WildCardQueenAdmin)
admin.site.register(WildCardAppearance, WildCardAppearanceAdmin)
admin.site.register(AppearanceType, AppearanceTypeAdmin)
