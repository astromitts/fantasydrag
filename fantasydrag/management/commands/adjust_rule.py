from django.core.management.base import BaseCommand
from fantasydrag.models import DefaultRule


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--rule',
            '-r',
            type=str,
            help='Name of rule to adjust',
        )
        parser.add_argument(
            '--points',
            '-p',
            type=int,
            help='Point value to adjust to',
        )

    def handle(self, *args, **options):

        if options['rule'] and options['points']:
            DefaultRule.objects.filter(name__icontains=options['rule']).update(point_value=options['points'])
        else:
            self.stdout.write(
                self.style.ERROR(
                    'You must provide a rule name AND a point value'
                )
            )
