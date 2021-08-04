from django.contrib import admin
from django import forms
from stats.models import (
    CanonicalQueenEpisodeScore,
    CanonicalQueenDragRaceScore,
    DragRaceDraftScore,
    EpisodeDraftScore,
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


class EpisodeDraftScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['participant', 'drag_race', 'episode', 'total_score', 'rank_tier', 'total_participants']
    list_filter = ['episodedraft__episode']


class DragRaceDraftScoreAdmin(admin.ModelAdmin):
    form = FormBase
    list_display = ['participant', 'drag_race', 'total_score', 'rank_tier', 'total_participants']
    list_filter = ['participant', 'drag_race']


admin.site.register(EpisodeDraftScore, EpisodeDraftScoreAdmin)
admin.site.register(DragRaceDraftScore, DragRaceDraftScoreAdmin)
admin.site.register(CanonicalQueenDragRaceScore, CanonicalQueenDragRaceScoreAdmin)
admin.site.register(CanonicalQueenEpisodeScore, CanonicalQueenEpisodeScoreAdmin)
admin.site.register(QueenEpisodeScore, QueenEpisodeScoreAdmin)
admin.site.register(QueenDragRaceScore, QueenDragRaceScoreAdmin)
admin.site.register(PanelistEpisodeScore, PanelistEpisodeScoreAdmin)
admin.site.register(PanelistDragRaceScore, PanelistDragRaceScoreAdmin)
