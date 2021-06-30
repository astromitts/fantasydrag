from django.urls import path

from fantasydrag.api import views

urlpatterns = [
    path('api/episode/<int:episode_id>/score/', views.NewsPostApi.as_view(), name='api_episode_scores'),
    path('api/episode/<int:episode_id>/setscored/', views.NewsPostApi.as_view(), name='api_episode_set_scored'),
    path('api/episode/<int:episode_id>/score/<int:score_id>/delete/', views.NewsPostApi.as_view(), name='api_episode_score_delete'),
]
