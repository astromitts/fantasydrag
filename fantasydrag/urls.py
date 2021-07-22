from django.urls import path

from fantasydrag import views

urlpatterns = [
    path('error/', views.Error.as_view(), name='error'),
    path('login/', views.LogIn.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('logout/', views.LogOut.as_view(), name='logout'),
    path('contact/', views.Contact.as_view(), name='contact'),
    path('', views.LandingPage.as_view(), name='home'),
    path('about/', views.About.as_view(), name='about'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('queens/search/', views.QueenList.as_view(), name='queen_list'),
    path('queens/<int:queen_id>/', views.QueenDetail.as_view(), name='queen_detail'),
    path('dragrace/new/', views.DragRaceAddEdit.as_view(), name='drag_race_new'),
    path('dragrace/edit/<int:dragrace_id>/', views.DragRaceAddEdit.as_view(), name='drag_race_edit'),
    path('panels/<int:dragrace_id>/', views.PublicPanelList.as_view(), name='panel_list'),
    path('panel/new/<int:dragrace_id>/', views.CreatePanel.as_view(), name='panel_create'),
    path('panel/<int:panel_id>/edit/', views.CreatePanel.as_view(), name='panel_edit'),
    path('panel/<int:panel_id>/', views.PanelStats.as_view(), name='panel_stats'),
    path('panel/<int:panel_id>/leave/', views.LeavePanel.as_view(), name='panel_leave'),
    path('panel/<uuid:panel_code>/', views.JoinPanel.as_view(), name='panel_join_link'),
    path('panel/invite/<uuid:panel_code>/', views.JoinPanel.as_view(), name='panel_invitation_link'),
    path('panel/<int:panel_id>/draft/', views.SetDrafts.as_view(), name='panel_set_drafts'),
    path(
        'panel/<int:panel_id>/panelist/<int:participant_id>/',
        views.ParticipantPanelStats.as_view(),
        name='participant_stats'
    ),
    path(
        'dragrace/<int:dragrace_id>/',
        views.DragRaceStats.as_view(),
        name='dragrace_stats'
    ),
    path(
        'rules/<str:drag_race_type>/',
        views.RulesList.as_view(),
        name='dragrace_rules'
    ),
    path(
        'episode/<int:episode_id>/draft/',
        views.EpisodeDraft.as_view(),
        name='set_episode_draft'
    ),
    path(
        'dragrace/<int:dragrace_id>/episode/redirect/',
        views.SetEpisodeRedirect.as_view(),
        name='set_episode_scores_redirect'
    ),
    path(
        'dragrace/episode/<int:episode_id>/',
        views.EpisodeDetail.as_view(),
        name='episode_detail'
    ),
    path(
        'dragrace/<int:dragrace_id>/episode/new/',
        views.CreateEpisode.as_view(),
        name='create_episode'
    ),
    path(
        'dragrace/<int:dragrace_id>/episode/<int:episode_id>/score/',
        views.SetEpisodeScores.as_view(),
        name='set_episode_scores'
    ),
    path(
        'dragrace/<int:dragrace_id>/episode/<int:episode_id>/wildcards/',
        views.WildCards.as_view(),
        name='set_episode_wildcards'
    ),
]
