from django.contrib import admin
from django import forms
from fantasydrag.models import (
    DragRace,
    Episode,
    Queen,
    Rule,
    Score,
    Participant,
    Panel,
    Draft,
    WildCardQueen,
)


class FormBase(forms.ModelForm):
    fields = '__all__'


class DragRaceForm(FormBase):
    pass


class QueenForm(FormBase):
    pass


class EpisodeForm(FormBase):
    pass


class RuleForm(FormBase):
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


class DragRaceAdmin(admin.ModelAdmin):
    form = DragRaceForm


class QueenAdmin(admin.ModelAdmin):
    form = QueenForm


class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeForm


class RuleAdmin(admin.ModelAdmin):
    form = RuleForm
    list_display = ['name', 'score_type', 'point_value', 'drag_race']
    list_editable = ['score_type', 'point_value']


class ScoreAdmin(admin.ModelAdmin):
    form = ScoreForm


class ParticipantAdmin(admin.ModelAdmin):
    form = ParticipantForm


class PanelAdmin(admin.ModelAdmin):
    form = PanelForm


class DraftAdmin(admin.ModelAdmin):
    form = PanelForm


class WildCardQueenAdmin(admin.ModelAdmin):
    form = WildCardQueenForm


admin.site.register(DragRace, DragRaceAdmin)
admin.site.register(Queen, QueenAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Panel, PanelAdmin)
admin.site.register(Draft, DraftAdmin)
admin.site.register(WildCardQueen, WildCardQueenAdmin)
