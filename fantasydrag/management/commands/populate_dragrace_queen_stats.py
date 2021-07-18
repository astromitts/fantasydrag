from django.core.management.base import BaseCommand
from fantasydrag.models import DragRace, Stats, Queen


class Command(BaseCommand):

    def handle(self, *args, **options):

        drs = DragRace.objects.exclude(status='pending').all()
        for drag_race in drs:
                Stats.set_dragrace_queen_stats(drag_race)

        for queen in Queen.objects.all():
            Stats.set_queen_master_stats(queen)
