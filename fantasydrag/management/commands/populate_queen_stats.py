from django.core.management.base import BaseCommand
from fantasydrag.models import Queen


class Command(BaseCommand):

    def handle(self, *args, **options):
        queens = Queen.objects.all()
        for queen in queens:
            stats = queen.stats
            queen.tier_score = stats['average']
            queen.total_score = stats['total']
            queen.score_data = stats['drag_races']
            queen.save()
