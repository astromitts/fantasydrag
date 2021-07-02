from django.urls import path

from fantasydrag.api import views

urlpatterns = [
    path('api/panel/<int:panel_id>/draft/', views.PanelDraftApi.as_view(), name='api_panel_draft'),
    path('api/episode/<int:episode_id>/score/', views.EpisodeApi.as_view(), name='api_episode_scores'),
    path('api/episode/<int:episode_id>/score/<int:score_id>/delete/', views.EpisodeApi.as_view(), name='api_episode_score_delete'),
]
