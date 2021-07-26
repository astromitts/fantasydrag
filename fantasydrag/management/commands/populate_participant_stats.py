from django.core.management.base import BaseCommand
from fantasydrag.models import DragRace, Panel
from stats.models import (
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        drag_races = DragRace.objects.exclude(status='pending')
        panels = Panel.objects.filter(drag_race__in=drag_races)
        for panel in panels:
            drag_race = panel.drag_race
            queens = drag_race.queens.all()
            viewing_participants = panel.participants.all()
            target_participants = panel.participants.all()

            for vp in viewing_participants:
                for queen in queens:
                    for episode in vp.episodes.filter(drag_race=drag_race).all():
                        queen_ep_score = QueenEpisodeScore.get_or_create(
                            queen=queen,
                            episode=episode,
                            viewing_participant=vp
                        )
                        queen_ep_score.set_total_score()
                    for panelist in target_participants:
                        panelist_ep_score = PanelistEpisodeScore.get_or_create(
                            viewing_participant=vp,
                            panel=panel,
                            panelist=panelist,
                            episode=episode
                        )
                        panelist_ep_score.set_total_score()

                    queen_dr_score = QueenDragRaceScore.get_or_create(
                        queen=queen,
                        drag_race=drag_race,
                        viewing_participant=vp
                    )
                    queen_dr_score.set_total_score()

                for panelist in target_participants:
                    panelist_dr_score = PanelistDragRaceScore.get_or_create(
                        viewing_participant=vp,
                        panel=panel,
                        panelist=panelist,
                        drag_race=drag_race
                    )
                    panelist_dr_score.set_total_score()
