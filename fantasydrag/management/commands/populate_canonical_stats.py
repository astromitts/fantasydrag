from django.core.management.base import BaseCommand
from fantasydrag.models import DragRace, EpisodeDraft
from stats.models import (
    CanonicalQueenEpisodeScore,
    CanonicalQueenDragRaceScore
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        drag_races = DragRace.objects.exclude(status='pending').all()
        for drag_race in drag_races:
            queens = drag_race.queens.all()
            episodes = drag_race.episode_set.all()
            for queen in queens:
                CanonicalQueenEpisodeScore.destroy(queen=queen, drag_race=drag_race)
                for episode in episodes:
                    episode_score = CanonicalQueenEpisodeScore.get_or_create(
                        queen=queen,
                        episode=episode,
                        drag_race=drag_race
                    )
                    episode_score.set_total_score()
                CanonicalQueenDragRaceScore.destroy(queen=queen, drag_race=drag_race)
                drag_race_score = CanonicalQueenDragRaceScore.get_or_create(
                    queen=queen, drag_race=drag_race
                )
                drag_race_score.set_total_score()
            for episode in episodes:
                episode_drafts = EpisodeDraft.objects.filter(episode=episode)
                for episode_draft in episode_drafts:
                    episode_draft.set_total_score()
