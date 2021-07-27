from django.contrib import admin
from django import forms
from stats.models import (
    CanonicalQueenEpisodeScore,
    CanonicalQueenDragRaceScore,
    PanelistDragRaceScore,
    PanelistEpisodeScore,
    QueenDragRaceScore,
    QueenEpisodeScore
)


class FormBase(forms.ModelForm):
    fields = '__all__'


class CanonicalQueenEpisodeScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['queen', 'drag_race', 'episode', 'total_score']
    list_filter = ['queen', 'drag_race', 'episode']


class CanonicalQueenDragRaceScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['queen', 'drag_race', 'total_score']
    list_filter = ['queen', 'drag_race']


class QueenEpisodeScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['viewing_participant', 'queen', 'episode', 'total_score']
    list_filter = list_display


class QueenDragRaceScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['viewing_participant', 'queen', 'drag_race', 'total_score']
    list_filter = list_display


class PanelistEpisodeScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['viewing_participant', 'panelist', 'episode', 'total_score']
    list_filter = list_display


class PanelistDragRaceScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['viewing_participant', 'panelist', 'drag_race', 'total_score']
    list_filter = list_display


admin.site.register(CanonicalQueenDragRaceScore, CanonicalQueenDragRaceScoreAdmin)
admin.site.register(CanonicalQueenEpisodeScore, CanonicalQueenEpisodeScoreAdmin)
admin.site.register(QueenEpisodeScore, QueenEpisodeScoreAdmin)
admin.site.register(QueenDragRaceScore, QueenDragRaceScoreAdmin)
admin.site.register(PanelistEpisodeScore, PanelistEpisodeScoreAdmin)
admin.site.register(PanelistDragRaceScore, PanelistDragRaceScoreAdmin)
