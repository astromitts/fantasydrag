from django.forms import (
    Form,
    CharField,
    PasswordInput,
    TextInput,
    IntegerField,
)


class LoginPasswordForm(Form):
    username = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))


class CreateEpisodeForm(Form):
    number = IntegerField(widget=TextInput(attrs={'class': 'form-control'}), required=True)
    title = CharField(widget=TextInput(attrs={'class': 'form-control'}), required=True)
