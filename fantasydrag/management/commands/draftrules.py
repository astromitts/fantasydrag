from django.core.management.base import BaseCommand
from fantasydrag.utils import calculate_draft_data
from fantasydrag.models import Panel
import pprint


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--queens',
            '-q',
            type=int,
            help='Number of queens to calculate for. Only works when no Panel ID is provided.',
        )
        parser.add_argument(
            '--participants',
            '-c',
            type=int,
            help='Number of participants to calculate for. Only works when no Panel ID is provided.',
        )
        parser.add_argument(
            '--panel',
            '-p',
            type=int,
            help='ID of a Panel instance calculate for',
        )

    def handle(self, *args, **options):
        pp = pprint.PrettyPrinter(indent=4)

        if options['panel']:
            panel = Panel.objects.get(pk=options['panel'])
            rule_set = panel.set_draft_rules()
        elif options['queens'] and options['participants']:
            rule_set = calculate_draft_data(
                participant_count=options['participants'],
                queen_count=options['queens']
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    'You must provide either a Panel ID OR a participant count AND queen count'
                )
            )

        pp.pprint(rule_set)
