from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.template.loader import render_to_string


class Mailer(object):

    @classmethod
    def send_mail(cls, to_email, subject, content, template=None, context=None):
        if template:
            if not context:
                context = {}
            html_body = render_to_string(
                template, context
            )
        else:
            html_body = content

        message = Mail(
            from_email=settings.EMAILS_FROM,
            to_emails=to_email,
            subject=subject,
            html_content=html_body
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response
