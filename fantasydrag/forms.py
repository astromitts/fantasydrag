from django.forms import (
    Form,
    CharField,
    PasswordInput,
    TextInput,
)


class LoginPasswordForm(Form):
    username = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
