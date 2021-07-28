from django.urls import path

from stats.api import views

urlpatterns = [
    path(
        'api/stats/dragrace/<int:dragrace_id>/queen/<int:queen_id>/',
        views.DragRaceQueenApiView.as_view(),
        name='api_stats_dragrace_queen'
    ),
    path(
        'api/stats/episode/<int:episode_id>/queen/<int:queen_id>/',
        views.EpisodeQueenApiView.as_view(),
        name='api_stats_episode_queen'
    ),
    path(
        'api/stats/panel/<int:panel_id>/episode/<int:episode_id>/',
        views.EpisodePanelApiView.as_view(),
        name='api_stats_episode_panel'
    ),
    path(
        'api/stats/panel/<int:panel_id>/episode/<int:episode_id>/panelist/<int:target_participant_id>/',
        views.EpisodePanelApiView.as_view(),
        name='api_stats_episode_panel'
    ),
    path(
        'api/stats/panel/<int:panel_id>/dragrace/',
        views.DragRacePanelApiView.as_view(),
        name='api_stats_dragrace_panel'
    ),
    path(
        'api/stats/dashboard/',
        views.StatsDashboardApiView.as_view(),
        name='api_stats_dashboard'

    ),
    path(
        'api/stats/episode/<int:episode_id>/<str:endpoint>/',
        views.StatsEpisodeScoreApiView.as_view(),
        name='api_stats_score'

    ),
]
