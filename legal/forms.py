from django.forms import (
    Form,
    CheckboxInput,
    BooleanField
)
from django.utils.safestring import mark_safe


class PolicyForm(Form):
    eula = BooleanField(
        widget=CheckboxInput(),
        label=mark_safe(
            'I have read and agree to the <a href="/end-user-license-agreement/">End User License Agreement</a>'
        ),
        required=True
    )
    pp = BooleanField(
        widget=CheckboxInput(),
        label=mark_safe(
            'I have read and agree to the <a href="/privacy-policy/">Privacy Policy</a>'
        ),
        required=True
    )
