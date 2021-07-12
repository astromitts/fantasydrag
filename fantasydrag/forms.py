from django.forms import (
    Form,
    CharField,
    PasswordInput,
    TextInput,
    EmailInput,
    IntegerField,
)


class LoginPasswordForm(Form):
    username = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))


class RegisterForm(Form):
    username = CharField(
        widget=TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'ng-model': 'username'
        }),
        help_text='This is how other particpants will identify you'
    )
    email = CharField(widget=EmailInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'ng-model': 'email'
    }))
    password = CharField(widget=PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'ng-model': 'newPassword'
    }))
    confirm_password = CharField(widget=PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'ng-model': 'confirmPassword'
    }))


class CreateEpisodeForm(Form):
    number = IntegerField(widget=TextInput(attrs={'class': 'form-control'}), required=True)
    title = CharField(widget=TextInput(attrs={'class': 'form-control'}), required=True)


class CreatePanelForm(Form):
    name = CharField(
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Name your panel',
        required=True)
