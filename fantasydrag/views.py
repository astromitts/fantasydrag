from django.contrib import messages
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
    DragRaceType,
    Episode,
    WildCardQueen,
)
from fantasydrag.stats import Stats
from fantasydrag.forms import (
    LoginPasswordForm,
    RegisterForm,
    CreateEpisodeForm,
    CreatePanelForm,
)
from fantasydrag.utils import refresh_dragrace_stats_for_participant


def _login(form, request):
    form = form(request.POST)
    error = None
    result = {
        'valid': True,
        'form': None
    }
    if form.is_valid():
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = User.objects.filter(username__iexact=username).first()
        if user:
            password_check = user.check_password(password)
            if password_check:
                login(request, user)
                request.session['user_is_authenticated'] = True
            else:
                error = 'Password did not match.'
        else:
            error = 'Username not found.'
    else:
        error = 'Invalid form submission.'
    if error:
        result['valid'] = False
    result['form'] = form
    result['error'] = '{} Please check your information and try again'.format(error)
    return result


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
        login_attempt = _login(self.form, request)
        if login_attempt['valid']:
            return redirect(reverse('home'))
        else:
            self.context.update(login_attempt)
        return HttpResponse(self.template.render(self.context, request))


class LogOut(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        request.session['user_is_authenticated'] = False
        return redirect(reverse('home'))


class AuthenticatedView(View):
    def setup(self, request, *args, **kwargs):
        super(AuthenticatedView, self).setup(request, *args, **kwargs)
        self.user = request.user
        if self.user.is_authenticated:
            try:
                self.participant = Participant.objects.get(user=self.user)
            except:
                self.participant = Participant.objects.get(display_name=self.user.username)
                self.participant.user = self.user
                self.participant.save()
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
            if 'episode_id' in kwargs:
                self.episode = Episode.objects.get(pk=kwargs['episode_id'])
                self.context.update(
                    {'episode': self.episode}
                )


class About(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/about.html')
        context = {}
        return HttpResponse(template.render(context, request))


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
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            template = loader.get_template('pages/dashboard/dashboard.html')
            self.context.update({
                'pageModule': 'dashboardModule',
                'pageController': 'dashboardController'
            })
        else:
            template = loader.get_template('pages/about.html')
            self.context = {
                'form': LoginPasswordForm()
            }
        return HttpResponse(template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        template = loader.get_template('pages/about.html')
        login_attempt = _login(LoginPasswordForm, request)
        if login_attempt['valid']:
            return redirect(reverse('home'))
        else:
            context = login_attempt
        return HttpResponse(template.render(context, request))


class RulesList(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/ruleslist.html')
        drtype = DragRaceType.objects.get(name=kwargs['drag_race_type'])
        context = {
            'drag_race_type': drtype
        }
        return HttpResponse(template.render(context, request))


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


class LeavePanel(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(LeavePanel, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/leave-panel.html')

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        self.panel.participants.remove(self.participant)
        messages.success(request, 'You successfully left the panel "{}"'.format(self.panel.name))
        return redirect(reverse('home'))


class JoinPanel(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(JoinPanel, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/join-panel.html')
        self.panel = Panel.objects.get(code=kwargs['panel_code'])
        self.invited = False
        if request.resolver_match.url_name == 'panel_invitation_link':
            self.invited = True

    def get(self, request, *args, **kwargs):
        if self.panel.panel_type == 'private' and not self.invited:
            messages.error(request, 'You must have a special invite link to join a private channel.')
            return redirect(reverse('panel_list', kwargs={'dragrace_id': self.panel.drag_race.pk}))
        self.context.update({
            'panel': self.panel,
            'invited': self.invited,
            'in_panel': self.participant in self.panel.participants.all()
        })
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        if self.panel.panel_type == 'private' and not self.invited:
            messages.error(request, 'You must have a special invite link to join a private channel.')
            return redirect(reverse('panel_list', kwargs={'dragrace_id': self.panel.drag_race.pk}))
        if self.panel.participant_limit > self.panel.available_slots:
            self.panel.participants.add(self.participant)
        else:
            messages.error(request, 'Panel is already full. Please find another panel to join or start a new one.')
            return redirect(reverse('panel_list', kwargs={'dragrace_id': self.panel.drag_race.pk}))
        return redirect(reverse('panel_stats', kwargs={'panel_id': self.panel.pk}))


class PublicPanelList(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        self.template = loader.get_template('pages/open-panels.html')
        self.context.update({
            'panels': self.drag_race.panel_set.filter(
                panel_type='public',
                status='open'
            ),
        })
        return HttpResponse(self.template.render(self.context, request))


class PanelStats(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(PanelStats, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('pages/panel/detail.html')

    def get(self, request, *args, **kwargs):
        queen_stats = Stats.objects.filter(
            participant=self.participant,
            panel=self.panel,
            stat_type='participant_queen_scores'
        ).order_by('-primary_stat').all()
        panel_stats = Stats.objects.filter(
            participant=self.participant,
            panel=self.panel,
            stat_type='dragrace_panel_scores'
        ).first()

        self.context.update({
            'queen_stats': queen_stats,
            'panel_stats': panel_stats,
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


class ParticipantPanelStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        panel = self.participant.panel_set.get(pk=kwargs['panel_id'])
        this_participant = panel.participants.get(pk=kwargs['participant_id'])
        template = loader.get_template('pages/panelistdetail.html')
        panel_stats = Stats.objects.filter(
            participant=self.participant,
            panel=self.panel,
            stat_type='dragrace_panel_scores'
        ).first()

        panelist_stats = {}
        for panel_stat in panel_stats.data:
            if panel_stat['participant']['pk'] == this_participant.pk:
                panelist_stats = panel_stat
        self.context.update({
            'this_participant': this_participant,
            'panelist_stats': panelist_stats
        })
        return HttpResponse(template.render(self.context, request))


class DragRaceStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/dragracedetail.html')
        queen_stats = Stats.objects.filter(
            participant=self.participant,
            drag_race=self.drag_race,
            panel=None,
            stat_type='participant_queen_scores'
        ).order_by('-primary_stat').all()
        wq_queen_stats = Stats.objects.filter(
            participant=self.participant,
            drag_race=self.drag_race,
            panel=None,
            stat_type='participant_wildqueen_scores'
        ).order_by('-primary_stat').all()
        scored_episodes = self.drag_race.episode_set.filter(is_scored=True).all()
        self.context.update({
            'viewed_episodes': self.participant.episodes.filter(drag_race=self.drag_race).all(),
            'scored_episodes': scored_episodes,
            'queen_stats': queen_stats,
            'wq_stats': wq_queen_stats
        })
        return HttpResponse(template.render(self.context, request))


class EpisodeDraft(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/generalteamdraft.html')
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
        elif 'hide' in request.POST:
            self.participant.episodes.remove(self.episode)

        self.participant.save()
        refresh_dragrace_stats_for_participant(self.participant, self.episode.drag_race)
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
        self.context.update({'form': self.form(initial={'number': (max_episode['number__max'] or 0) + 1})})
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
        stats = Stats.objects.filter(
            queen=queen,
            participant=self.participant,
            stat_type='queen_scores'
        ).first()
        self.context.update(
            {
                'queen': queen,
                'stats': stats,
                'viewed_episodes': [episode.pk for episode in self.participant.episodes.all()]
            }
        )
        return HttpResponse(self.template.render(self.context, request))


class QueenList(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        self.template = loader.get_template('pages/queenlist.html')
        return HttpResponse(self.template.render(self.context, request))
