from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.db.models import Max
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader
from django.views import View
from django.db import IntegrityError
from fantasydrag.models import (
    Panel,
    Participant,
    Queen,
    DragRace,
    Episode,
    WildCardQueen,
)
from fantasydrag.forms import (
    LoginPasswordForm,
    RegisterForm,
    CreateEpisodeForm,
    CreatePanelForm,
)


class Error(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('error.html')
        context = {}
        return HttpResponse(template.render(context, request))


class Register(View):
    def setup(self, request, *args, **kwargs):
        super(Register, self).setup(request, *args, **kwargs)
        self.form = RegisterForm
        self.template = loader.get_template('pages/register.html')
        self.context = {'form': None, 'error': None}

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.form()
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        error = None
        if form.is_valid():
            self.context['form'] = form
        else:
            error = 'Invalid form submission.'
        self.context['form'] = form
        self.context['error'] = '{} Please check your information and try again'.format(error)
        return HttpResponse(self.template.render(self.context, request))


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

        if 'dragrace_id' in kwargs:
            self.drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
            self.context.update(
                {'drag_race': self.drag_race}
            )


class Profile(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/profile.html')
        return HttpResponse(template.render(self.context, request))


class DragRaceAddEdit(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        dragrace_id = kwargs.get('dragrace_id')
        template = loader.get_template('pages/newdragrace.html')
        self.context.update({'dragrace_id': dragrace_id})
        return HttpResponse(template.render(self.context, request))


class LandingPage(AuthenticatedView):

    def _format_drag_races(self, drag_races):
        formatted_drag_races = {}
        for drag_race in drag_races:
            formatted_drag_races[drag_race] = {'participant_panels': []}
            formatted_drag_races[drag_race]['participant_panels'] = self.participant.panel_set.filter(
                drag_race=drag_race).all()
        return formatted_drag_races

    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/dashboard/dashboard.html')
        current_races = DragRace.objects.filter(is_current=True).order_by('-season').all()
        past_races = DragRace.objects.filter(is_current=False).order_by('-season').all()
        formatted_current_races = self._format_drag_races(current_races)
        formatted_past_races = self._format_drag_races(past_races)
        self.context.update({
            'current_drag_races': formatted_current_races,
            'past_drag_races': formatted_past_races
        })
        return HttpResponse(template.render(self.context, request))


class RulesList(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/ruleslist.html')

        drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
        rules = drag_race.drag_race_type.defaultrule_set.all()
        self.context.update({
            'drag_race': drag_race,
            'rules': rules
        })
        return HttpResponse(template.render(self.context, request))


class CreatePanel(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(CreatePanel, self).setup(request, *args, **kwargs)
        self.form = CreatePanelForm
        self.template = loader.get_template('pages/create-panel.html')

    def get(self, request, *args, **kwargs):
        self.context.update({'form': self.form()})
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            try:
                panel = Panel(
                    drag_race=self.drag_race,
                    name=request.POST['name'],
                    participant_limit=request.POST['participant_limit'],
                    panel_type=request.POST['panel_type'],
                    wildcard_allowance=request.POST['wildcard_allowance']
                )
                panel.save()
                panel.participants.add(self.participant)
                panel.captains.add(self.participant)
                panel.save()
                return redirect(reverse('panel_stats', kwargs={'panel_id': panel.pk}))
            except IntegrityError:
                error = 'A panel with this name already exists for {}'.format(self.drag_race.display_name)
        else:
            error = 'Invalid submission. Please check your form and try again.'
        self.context.update(
            {
                'error': error,
                'form': form
            }
        )
        return HttpResponse(self.template.render(self.context, request))


class JoinPanel(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(JoinPanel, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/join-panel.html')
        self.panel = Panel.objects.get(code=kwargs['panel_code'])

    def get(self, request, *args, **kwargs):
        self.context.update({
            'panel': self.panel,
            'in_panel': self.participant in self.panel.participants.all()
        })
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        self.panel.participants.add(self.participant)
        return redirect(reverse('panel_stats', kwargs={'panel_id': self.panel.pk}))


class PanelStats(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(PanelStats, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/paneldetail.html')

    def get(self, request, *args, **kwargs):
        queen_scores = Queen.get_formatted_scores_for_drag_race(self.panel.drag_race, self.participant)

        self.context.update({
            'queen_scores': queen_scores,
            'panel_scores': self.panel.get_formatted_scores_for_panelists(self.participant),
            'join_link': self.panel.get_join_link(request)
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


class Episodes(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        self.template = loader.get_template('pages/episodemanager.html')
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


class CreateEpisode(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(CreateEpisode, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/create-episode.html')
        self.form = CreateEpisodeForm

    def get(self, request, *args, **kwargs):
        max_episode = self.drag_race.episode_set.aggregate(Max('number'))
        self.context.update({'form': self.form(initial={'number': max_episode['number__max'] + 1})})
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            try:
                new_episode = Episode(
                    drag_race=self.drag_race,
                    number=request.POST['number'],
                    title=request.POST['title']
                )
                new_episode.save()
                return redirect(
                    reverse(
                        'set_episode_scores',
                        kwargs={
                            'dragrace_id': self.drag_race.pk,
                            'episode_id': new_episode.pk,
                        }
                    )
                )
            except IntegrityError:
                error = 'Episode #{} for {} already exists'.format(
                    request.POST['number'], self.drag_race.display_name
                )
        self.context.update({
            'form': form,
            'error': error,
        })
        return HttpResponse(self.template.render(self.context, request))


class WildCards(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(WildCards, self).setup(request, *args, **kwargs)
        self.episode = Episode.objects.get(pk=kwargs['episode_id'], drag_race__id=kwargs['dragrace_id'])
        self.context.update({'episode': self.episode})
        self.template = loader.get_template('pages/episodewildcards.html')

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


class QueenDetail(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        self.template = loader.get_template('pages/queendetail.html')
        queen = Queen.objects.get(pk=kwargs['queen_id'])
        stats = queen.formatted_stats
        self.context.update({'queen': queen, 'stats': stats})
        return HttpResponse(self.template.render(self.context, request))


class QueenList(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        self.template = loader.get_template('pages/queenlist.html')
        return HttpResponse(self.template.render(self.context, request))
