from django.contrib.auth.models import User
from django.contrib.auth import login
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
    Score,
    WildCardQueen
)
from fantasydrag.forms import LoginPasswordForm


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
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = User.objects.get(username=username)
            if user:
                password_check = user.check_password(password)
                if password_check:
                    login(request, user)
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


class LandingPage(AuthenticatedView):

    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/dashboard.html')
        self.context.update({
            'panels': self.participant.panel_set.all()
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
            self.panel.start_draft()
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
        self.queens = self.panel.drag_race.queens.all()
        self.drafts = self.panel.draft_set.all()
        queens_by_draft_count = {}
        for draft in self.drafts:
            this_count = queens_by_draft_count.get(draft.queen, 0)
            this_count += 1
            queens_by_draft_count[draft.queen] = this_count

        self.available_queens = []
        for queen in self.queens:
            if queens_by_draft_count.get(queen, 0) < self.panel.queen_draft_allowance:
                self.available_queens.append(queen)

        self.phase = 'set player'
        self.context.update({
            'queens': self.available_queens,
            'drafts': self.drafts,
            'phase': self.phase,
            'draft_participant': None,
        })
        self.template = loader.get_template('pages/setdrafts.html')

    def get(self, request, *args, **kwargs):
        if self.panel.status == 'open':
            self.panel.start_draft()
        self.context['phase'] = 'set queen'
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        participant = self.panel.current_draft_player
        if request.POST.get('queen'):
            queen = Queen.objects.get(pk=request.POST.get('queen'))
            self.panel.save_player_draft(participant, queen)
            self.context['phase'] = 'advance'
            self.context['drafts'] = self.panel.draft_set.all()
        elif request.POST.get('skip'):
            self.context['phase'] = 'set queen'
            self.panel.advance_draft()
        elif request.POST.get('advancedraft'):
            self.panel.advance_draft()
            participant = self.panel.current_draft_player
            self.context['phase'] = 'set queen'
        elif request.POST.get('selectagain'):
            self.context['phase'] = 'set queen'
        elif request.POST.get('advanceround'):
            self.context['phase'] = 'set queen'
            self.panel.advance_round()
        elif request.POST.get('enddraft'):
            self.panel.end_draft()
            return redirect(reverse('panel_stats', kwargs={'panel_id': self.panel.pk}))

        self.context['draft_participant'] = participant
        participant_drafts = self.panel.draft_set.filter(participant=participant)
        drafted_queens = [pd.queen for pd in participant_drafts]
        self.available_queens = [q for q in self.available_queens if q not in drafted_queens]
        self.context['queens'] = self.available_queens

        return HttpResponse(self.template.render(self.context, request))


class ParticipantStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        panel = self.participant.panel_set.get(pk=kwargs['panel_id'])
        this_participant = panel.participants.get(pk=kwargs['participant_id'])
        template = loader.get_template('pages/panelistdetail.html')
        scores = this_participant.get_formatted_scores_for_panel(panel, self.participant)
        self.context.update({
            'this_participant': this_participant,
            'draft_scores': scores,
            'total_score': sum([v for d, v in scores.items()])
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

    def post(self, request, *args, **kwargs):
        if self.is_site_admin:
            if 'deletescore' in request.POST:
                Score.objects.get(episode=self.episode, pk=request.POST['score']).delete()
                return redirect(
                    reverse(
                        'set_episode_scores',
                        kwargs={'dragrace_id': self.episode.drag_race.pk, 'episode_id': self.episode.pk}
                    )
                )
            elif 'addscore' in request.POST:
                queen = self.episode.drag_race.queens.get(pk=request.POST['queen'])
                rule = self.episode.drag_race.rule_set.get(pk=request.POST['rule'])
                new_score = Score(
                    episode=self.episode,
                    rule=rule,
                    queen=queen
                )
                new_score.save()
            elif 'setscored' in request.POST:
                self.episode.is_scored = True
                self.episode.save()
            elif 'unsetscored' in request.POST:
                self.episode.is_scored = False
                self.episode.save()

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
