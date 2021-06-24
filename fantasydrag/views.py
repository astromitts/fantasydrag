from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader
from django.views import View
from fantasydrag.models import Participant, Queen, Draft, DragRace


class AuthenticatedView(View):
    def setup(self, request, *args, **kwargs):
        super(AuthenticatedView, self).setup(request, *args, **kwargs)
        self.user = request.user
        self.participant = Participant.objects.get(user=self.user)


class LandingPage(AuthenticatedView):

    def get(self, request, *args, **kwargs):
        template = loader.get_template('pages/dashboard.html')
        context = {
            'participant': self.participant,
            'panels': self.participant.panel_set.all()
        }
        return HttpResponse(template.render(context, request))


class PanelStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        panel = self.participant.panel_set.get(pk=kwargs['panel_id'])
        template = loader.get_template('pages/paneldetail.html')
        queen_scores = Queen.get_formatted_scores_for_drag_race(panel.drag_race)

        context = {
            'participant': self.participant,
            'panel': panel,
            'queen_scores': queen_scores,
            'panel_scores': panel.get_formatted_scores_for_panelists()
        }

        return HttpResponse(template.render(context, request))


class SetDrafts(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(SetDrafts, self).setup(request, *args, **kwargs)
        self.user = request.user
        self.panel = self.participant.panel_set.get(pk=kwargs['panel_id'])
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
        self.context = {
            'panel': self.panel,
            'queens': self.available_queens,
            'drafts': self.drafts,
            'phase': self.phase,
            'participant': None,
        }
        self.template = loader.get_template('pages/setdrafts.html')

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        participant = Participant.objects.get(pk=request.POST['participant'])
        if request.POST.get('queen'):
            queen = Queen.objects.get(pk=request.POST.get('queen'))
        else:
            queen = None
        if not queen:
            self.context['phase'] = 'set queen'
            self.context['participant'] = participant
            participant_drafts = self.panel.draft_set.filter(participant=participant)
            drafted_queens = [pd.queen for pd in participant_drafts]
            self.available_queens = [q for q in self.available_queens if q not in drafted_queens]
            self.context['queens'] = self.available_queens
            return HttpResponse(self.template.render(self.context, request))
        else:
            new_draft = Draft(
                participant=participant,
                queen=queen,
                panel=self.panel
            )
            new_draft.save()
        return redirect(reverse('panel_set_drafts', kwargs={'panel_id': self.panel.pk}))


class ParticipantStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        panel = self.participant.panel_set.get(pk=kwargs['panel_id'])
        participant = panel.participants.get(pk=kwargs['participant_id'])
        template = loader.get_template('pages/panelistdetail.html')
        scores = participant.get_formatted_scores_for_panel(panel)
        context = {
            'panel': panel,
            'participant': participant,
            'draft_scores': scores,
            'total_score': sum([v for d, v in scores.items()])
        }
        return HttpResponse(template.render(context, request))


class DragRaceStats(AuthenticatedView):
    def get(self, request, *args, **kwargs):
        drag_race = DragRace.objects.get(pk=kwargs['dragrace_id'])
        template = loader.get_template('pages/dragracedetail.html')
        scores = drag_race.get_scores_by_episode()
        context = {
            'drag_race': drag_race,
            'scores': scores
        }
        return HttpResponse(template.render(context, request))
