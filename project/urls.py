"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from fantasydrag import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('error/', views.Error.as_view(), name='error'),
    path('login/', views.LogIn.as_view(), name='login'),
    path('logout/', views.LogOut.as_view(), name='logout'),
    path('', views.LandingPage.as_view(), name='home'),
    path('panel/<int:panel_id>/', views.PanelStats.as_view(), name='panel_stats'),
    path('panel/<int:panel_id>/setdrafts/', views.SetDrafts.as_view(), name='panel_set_drafts'),
    path('panel/<int:panel_id>/wildcards/', views.WildCardList.as_view(), name='panel_wildcards'),
    path('panel/<int:panel_id>/setdrafts/random/', views.AssignRandomDrafts.as_view(), name='panel_set_random_drafts'),
    path(
        'panel/<int:panel_id>/panelist/<int:participant_id>/',
        views.ParticipantStats.as_view(),
        name='participant_stats'
    ),
    path(
        'dragrace/<int:dragrace_id>/',
        views.DragRaceStats.as_view(),
        name='dragrace_stats'
    ),
    path(
        'dragrace/<int:dragrace_id>/rules/',
        views.RulesList.as_view(),
        name='dragrace_rules'
    ),
    path(
        'dragrace/<int:dragrace_id>/episode/redirect',
        views.SetEpisodeRedirect.as_view(),
        name='set_episode_scores_redirect'
    ),
    path(
        'dragrace/episode/<int:episode_id>/',
        views.EpisodeDetail.as_view(),
        name='episode_detail'
    ),
    path(
        'dragrace/<int:dragrace_id>/episode/<int:episode_id>/score/',
        views.SetEpisodeScores.as_view(),
        name='set_episode_scores'
    ),
]
