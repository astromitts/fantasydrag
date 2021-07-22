from django.forms import (
    Form,
    CharField,
    ChoiceField,
    Select
)
from django_summernote.widgets import SummernoteWidget


class ContactForm(Form):
    message_type = ChoiceField(
        widget=Select(
            attrs={
                'class': 'form-control',
                'ng-model': 'messageType',
                'required': True
            }
        ),
        choices=(
            ('support', 'Support'),
            ('dispute', 'Dispute a score'),
            ('general', 'General')
        ),
        required=True
    )
    dispute_type = ChoiceField(
        widget=Select(
            attrs={
                'class': 'form-control',
            }
        ),
        choices=(
            ('wrong', 'A score is wrong'),
            ('missing', 'A score is missing')
        )
    )
    content = CharField(widget=SummernoteWidget(), required=True)
