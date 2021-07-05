from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader
from django.views import View
from fantasydrag.models import (
    Participant,
    Queen,
    DragRace,
    Episode,
    WildCardQueen,
)
from fantasydrag.forms import LoginPasswordForm


class Error(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('error.html')
        context = {}
        return HttpResponse(template.render(context, request))


class LogIn(View):
    def setup(self, request, *args, **kwargs):
        super(LogIn, self).setup(request, *args, **kwargs)
        self.form = LoginPasswordForm
        self.template = loader.get_template('pages/login.html')
        self.context = {'form': None, 'error': None}

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.form()
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        error = None
        if form.is_valid():
            username = request.POST.get('username').lower()
            password = request.POST.get('password')
            user = User.objects.get(username__iexact=username)
            if user:
                password_check = user.check_password(password)
                if password_check:
                    login(request, user)
                    request.session['user_is_authenticated'] = True
                    return redirect(reverse('home'))
                else:
                    error = 'Password did not match.'
            else:
                error = 'Username not found.'
        else:
            error = 'Invalid form submission.'
        self.context['form'] = form
        self.context['error'] = '{} Please check your information and try again'.format(error)
        return HttpResponse(self.template.render(self.context, request))


class LogOut(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        request.session['user_is_authenticated'] = False
        return redirect(reverse('login'))


class AuthenticatedView(View):
    def setup(self, request, *args, **kwargs):
        super(AuthenticatedView, self).setup(request, *args, **kwargs)
        self.user = request.user
        self.participant = Participant.objects.get(user=self.user)
        self.is_site_admin = self.participant.site_admin
        self.context = {
            'participant': self.participant,
            'is_site_admin': self.is_site_admin
        }
        if 'panel_id' in kwargs:
            self.panel = self.participant.panel_set.get(pk=kwargs['panel_id'])
            self.is_captain = self.participant in self.panel.captains.all()
            self.context.update(
                {
                    'is_captain': self.is_captain,
                    'panel': self.panel
                }
            )


class Profile(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/profile.html')
        return HttpResponse(template.render(self.context, request))


class LandingPage(AuthenticatedView):

    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/dashboard.html')
        all_races = DragRace.objects.all()

        formatted_races = {}
        for drag_race in all_races:
            formatted_races[drag_race] = {'participant_panels': []}
            formatted_races[drag_race]['participant_panels'] = self.participant.panel_set.filter(
                drag_race=drag_race).all()
        self.context.update({
            'drag_races': formatted_races
        })
        return HttpResponse(template.render(self.context, request))


class RulesList(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/ruleslist.html')

        drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
        self.context.update({
            'drag_race': drag_race
        })
        return HttpResponse(template.render(self.context, request))


class PanelStats(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(PanelStats, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/paneldetail.html')

    def get(self, request, *args, **kwargs):
        queen_scores = Queen.get_formatted_scores_for_drag_race(self.panel.drag_race, self.participant)

        self.context.update({
            'queen_scores': queen_scores,
            'panel_scores': self.panel.get_formatted_scores_for_panelists(self.participant)
        })

        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        if 'resetdraft' in request.POST and self.is_captain:
            self.panel.reset_draft()
        return redirect(reverse('panel_stats', kwargs={'panel_id': self.panel.pk}))


class AssignRandomDrafts(AuthenticatedView):
    def post(self, request, *args, **kwargs):
        if self.is_captain:
            self.panel.set_random_drafts()
        return redirect(reverse('panel_stats', kwargs={'panel_id': self.panel.pk}))


class SetDrafts(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(SetDrafts, self).setup(request, *args, **kwargs)
        self.user = request.user
        self.template = loader.get_template('pages/setdrafts/setdrafts.html')

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))


class ParticipantStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        panel = self.participant.panel_set.get(pk=kwargs['panel_id'])
        this_participant = panel.participants.get(pk=kwargs['participant_id'])
        template = loader.get_template('pages/panelistdetail.html')
        scores = this_participant.get_all_formatted_scores_for_panel(panel, self.participant)
        self.context.update({
            'this_participant': this_participant,
            'scores': scores
        })
        return HttpResponse(template.render(self.context, request))


class DragRaceStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
        template = loader.get_template('pages/dragracedetail.html')
        scores = drag_race.get_scores_by_episode(self.participant)
        self.context.update({
            'drag_race': drag_race,
            'scores': scores
        })
        return HttpResponse(template.render(self.context, request))


class SetEpisodeRedirect(AuthenticatedView):
    def post(self, request, *args, **kwargs):
        self.episode = Episode.objects.get(pk=request.POST['episode'], drag_race__id=kwargs['dragrace_id'])
        return redirect(
            reverse(
                'set_episode_scores',
                kwargs={'dragrace_id': self.episode.drag_race.pk, 'episode_id': self.episode.pk}
            )
        )


class EpisodeDetail(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(EpisodeDetail, self).setup(request, *args, **kwargs)
        self.episode = Episode.objects.get(pk=kwargs['episode_id'])
        self.template = loader.get_template('pages/episodedetail.html')
        self.context.update({
            'drag_race': self.episode.drag_race,
            'scores': self.episode.score_set.all(),
            'episode_is_visible': self.episode in self.participant.episodes.all(),
            'episode': self.episode
        })

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        if 'ruveal' in request.POST:
            self.participant.episodes.add(self.episode)
            self.participant.save()
        elif 'hide' in request.POST:
            self.participant.episodes.remove(self.episode)
            self.participant.save()
        self.context['episode_is_visible'] = self.episode in self.participant.episodes.all()
        return HttpResponse(self.template.render(self.context, request))


class SetEpisodeScores(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(SetEpisodeScores, self).setup(request, *args, **kwargs)
        self.episode = Episode.objects.get(pk=kwargs['episode_id'], drag_race__id=kwargs['dragrace_id'])
        self.template = loader.get_template('pages/setepisodescores.html')
        self.context.update({
            'drag_race': self.episode.drag_race,
            'scores': self.episode.score_set.all(),
            'episode': self.episode
        })

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))


class WildCardList(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(WildCardList, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/wildcardlist.html')
        self.queens = Queen.objects.exclude(pk__in=[q.pk for q in self.panel.drag_race.queens.all()])

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        if 'addwildqueen' in request.POST:
            this_participant = Participant.objects.get(pk=request.POST['participant'])
            queen = Queen.objects.get(pk=request.POST['wildcard_queen'])
            new_wcq = WildCardQueen(
                queen=queen,
                participant=this_participant,
                panel=self.panel
            )
            new_wcq.save()
        return redirect(reverse('panel_wildcards', kwargs={'panel_id': self.panel.pk}))
