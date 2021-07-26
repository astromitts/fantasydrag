from django.contrib import admin
from django import forms
from stats.models import (
    PanelistDragRaceScore,
    PanelistEpisodeScore,
    QueenDragRaceScore,
    QueenEpisodeScore
)


class FormBase(forms.ModelForm):
    fields = '__all__'


class QueenEpisodeScoreForm(FormBase):
    pass


class QueenEpisodeScoreAdmin(admin.ModelAdmin):
    form = QueenEpisodeScoreForm
    list_display = ['viewing_participant', 'queen', 'episode', 'total_score']
    list_filter = list_display


class QueenDragRaceScoreForm(FormBase):
    pass


class QueenDragRaceScoreAdmin(admin.ModelAdmin):
    form = QueenDragRaceScoreForm
    list_display = ['viewing_participant', 'queen', 'drag_race', 'total_score']
    list_filter = list_display


class PanelistEpisodeScoreForm(FormBase):
    pass


class PanelistEpisodeScoreAdmin(admin.ModelAdmin):
    form = PanelistEpisodeScoreForm
    list_display = ['viewing_participant', 'panelist', 'episode', 'total_score']
    list_filter = list_display


class PanelistDragRaceScoreForm(FormBase):
    pass


class PanelistDragRaceScoreAdmin(admin.ModelAdmin):
    form = PanelistDragRaceScoreForm
    list_display = ['viewing_participant', 'panelist', 'drag_race', 'total_score']
    list_filter = list_display


admin.site.register(QueenEpisodeScore, QueenEpisodeScoreAdmin)
admin.site.register(QueenDragRaceScore, QueenDragRaceScoreAdmin)
admin.site.register(PanelistEpisodeScore, PanelistEpisodeScoreAdmin)
admin.site.register(PanelistDragRaceScore, PanelistDragRaceScoreAdmin)
