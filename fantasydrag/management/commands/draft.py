from django.core.management.base import BaseCommand
from fantasydrag.models import Panel


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--panel',
            '-p',
            type=int,
            help='ID of a Panel instance calculate for',
        )
        parser.add_argument(
            '--command',
            '-c',
            type=str,
            help='Command to run [reset, start, advance or end]'
        )

    def handle(self, *args, **options):
        if options['panel'] and options['command']:
            panel = Panel.objects.get(pk=options['panel'])
            command = options['command']
        else:
            self.stdout.write(
                self.style.ERROR(
                    'You must provide a Panel ID and a command'
                )
            )

        if command == 'reset':
            panel.reset_draft()
        elif command == 'start':
            panel.start_draft()
        elif command == 'advance':
            panel.advance_draft()
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Command not recognized'
                )
            )
