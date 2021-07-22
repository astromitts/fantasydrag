from django.core.management.base import BaseCommand
from fantasydrag.tasks.tasks import start_drafts
from messagecenter.mailer import Mailer


class Command(BaseCommand):

    def handle(self, *args, **options):
        panels = start_drafts(testing=True)
        for panel in panels:
            participants = panel.participants.all()
            for participant in participants:
                content = '''
                    Hello hello hello, {}!<br />
                    Kittygirl here, reminding you that your Drag Crush draft for panel "{}" has started!<br />
                    Click here to join:
                    <a href="https://www.dragcrush.com{}" target="_blank">https://www.dragcrush.com{}</a>
                '''.format(
                    participant.display_name,
                    panel.name,
                    panel.draft_url,
                    panel.draft_url
                )
                Mailer.send_mail(
                    to_email=participant.email,
                    subject='Your Drag Crush draft for panel "{}" has started!'.format(panel.name),
                    content=content
                )
