from django.core.management.base import BaseCommand
from fantasydrag.models import DragRace
from stats.utils import set_episode_draft_scores


class Command(BaseCommand):

    def handle(self, *args, **options):
        drag_races = [DragRace.objects.get(pk=1), ]
        for drag_race in drag_races:
            for episode in drag_race.episode_set.all():
                set_episode_draft_scores(episode)
