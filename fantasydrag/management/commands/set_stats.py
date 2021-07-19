from django.core.management.base import BaseCommand
from fantasydrag.models import (
    EpisodeDraft,
    Panel,
    Queen,
    Participant,
)
from fantasydrag.stats import Stats


class Command(BaseCommand):

    def handle(self, *args, **options):
        Stats.objects.all().delete()
        panels = Panel.objects.exclude(drag_race__status='pending').all()
        unique_drag_races = []
        self.stdout.write('Setting panel specific stats...')
        for panel in panels:
            if panel.drag_race not in unique_drag_races:
                unique_drag_races.append(panel.drag_race)
            self.stdout.write('Setting participant stats for panel "{}"'.format(panel.name))
            for participant in panel.participants.all():
                self.stdout.write('Setting participant "{}" stats for panel "{}"'.format(
                    participant.display_name, panel.name))
                Stats.set_dragrace_draft_scores(
                    participant=participant,
                    drag_race=panel.drag_race
                )
                Stats.set_dragrace_panel_scores(
                    viewing_participant=participant,
                    panel=panel
                )
                Stats.set_participant_queen_scores(
                    viewing_participant=participant,
                    panel=panel
                )
                Stats.set_participant_wildqueen_scores(
                    viewing_participant=participant,
                    panel=panel
                )
                for drag_race in unique_drag_races:
                    Stats.set_participant_queen_scores(
                        viewing_participant=participant,
                        drag_race=drag_race
                    )
                    Stats.set_participant_wildqueen_scores(
                        viewing_participant=participant,
                        drag_race=drag_race
                    )

        for drag_race in unique_drag_races:
            self.stdout.write('Setting drag race draft stats for "{}"'.format(drag_race.display_name))
            dragrace_drafts = EpisodeDraft.objects.filter(episode__drag_race=drag_race).all()
            unique_participants = []
            for draft in dragrace_drafts:
                if draft.participant not in unique_participants:
                    unique_participants.append(draft.participant)
                    Stats.set_dragrace_participant_ranks(drag_race, draft.participant)

            Stats.set_dragrace_queen_stats(drag_race)

        for queen in Queen.objects.all():
            for participant in Participant.objects.all():
                self.stdout.write('Setting queen "{}" stats for participant "{}"'.format(
                    queen.name, participant.display_name))
                Stats.set_queen_master_stats(queen, participant)
