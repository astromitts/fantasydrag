from django.core.management.base import BaseCommand
from fantasydrag.models import DragRace, Participant
from stats.utils import set_viewing_participant_scores


class Command(BaseCommand):

    def handle(self, *args, **options):
        drag_races = [DragRace.objects.get(pk=1), ]
        for drag_race in drag_races:
            viewing_participants = Participant.objects.all()
            for vp in viewing_participants:
                set_viewing_participant_scores(vp, drag_race, True)
