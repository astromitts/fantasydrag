from django.urls import path

from fantasydrag.api import views

urlpatterns = [
    path('api/profile/', views.ProfileApi.as_view(), name='api_profile'),
    path('api/register/', views.RegisterApi.as_view(), name='api_register'),
    path('api/dragrace/', views.DragRaceApi.as_view(), name='api_drag_race'),
    path('api/dragrace/<int:dragrace_id>/', views.DragRaceApi.as_view(), name='api_drag_race'),
    path('api/defaultrules/', views.DefaultRulesApi.as_view(), name='api_default_rules'),
    path('api/queens/', views.QueenApi.as_view(), name='api_queens'),
    path('api/queens/search/', views.QueenSearchApi.as_view(), name='api_queen_search'),
    path('api/appearancetypes/', views.AppearanceTypeApi.as_view(), name='api_appearance_types'),
    path(
        'api/panel/<int:panel_id>/availablequeens/',
        views.DraftAvailableQueensApi.as_view(),
        name='api_panel_queens'
    ),
    path('api/panel/<int:panel_id>/drafts/', views.DraftMetaApi.as_view(), name='api_panel_draft_list'),
    path('api/panel/<int:panel_id>/draft/', views.PanelDraftApi.as_view(), name='api_panel_draft'),
    path('api/episode/<int:episode_id>/draft/', views.EpisodeDraftApi.as_view(), name='api_episode_draft'),
    path('api/episode/<int:episode_id>/score/', views.EpisodeApi.as_view(), name='api_episode_scores'),
    path('api/episode/<int:episode_id>/appearances/', views.EpisodeAppearanceApi.as_view(), name='api_episode_wqs'),
    path(
        'api/episode/<int:episode_id>/appearances/<int:wqa_id>/delete/',
        views.EpisodeAppearanceApi.as_view(),
        name='api_episode_wqs_delete'
    ),
    path(
        'api/episode/<int:episode_id>/score/<int:score_id>/delete/',
        views.EpisodeApi.as_view(),
        name='api_episode_score_delete'
    ),
    path(
        'api/panel/<int:panel_id>/edit/',
        views.CreatePanelApi.as_view(),
        name='api_create_edit'
    ),
    path(
        'api/dragrace/<int:dragrace_id>/panel/create/',
        views.CreatePanelApi.as_view(),
        name='api_create_panel'
    ),
]
