from django.urls import path

from fantasydrag.api import views

urlpatterns = [
    path('api/profile/', views.ProfileApi.as_view(), name='api_profile'),
    path('api/dragrace/', views.DragRaceApi.as_view(), name='api_drag_race'),
    path('api/dragrace/<int:dragrace_id>/', views.DragRaceApi.as_view(), name='api_drag_race'),
    path('api/defaultrules/', views.DefaultRulesApi.as_view(), name='api_default_rules'),
    path('api/queens/', views.QueenApi.as_view(), name='api_queens'),
    path(
        'api/panel/<int:panel_id>/availablequeens/',
        views.DraftAvailableQueensApi.as_view(),
        name='api_panel_queens'
    ),
    path('api/panel/<int:panel_id>/drafts/', views.DraftMetaApi.as_view(), name='api_panel_draft_list'),
    path('api/panel/<int:panel_id>/draft/', views.PanelDraftApi.as_view(), name='api_panel_draft'),
    path('api/episode/<int:episode_id>/score/', views.EpisodeApi.as_view(), name='api_episode_scores'),
    path(
        'api/episode/<int:episode_id>/score/<int:score_id>/delete/',
        views.EpisodeApi.as_view(),
        name='api_episode_score_delete'
    ),
]
