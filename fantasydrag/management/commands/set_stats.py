from django.core.management.base import BaseCommand
from fantasydrag.models import (
    EpisodeDraft,
    Panel,
    Stats,
    Queen,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        panels = Panel.objects.exclude(drag_race__status='pending').all()
        unique_drag_races = []
        for panel in panels:
            if panel.drag_race not in unique_drag_races:
                unique_drag_races.append(panel.drag_race)
            for participant in panel.participants.all():
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
                for drag_race in unique_drag_races:
                    Stats.set_participant_queen_scores(
                        viewing_participant=participant,
                        drag_race=drag_race
                    )

        for drag_race in unique_drag_races:
            EpisodeDraft.set_dragrace_stats(drag_race)
            Stats.set_dragrace_queen_stats(drag_race)

        for queen in Queen.objects.all():
            Stats.set_queen_master_stats(queen)
