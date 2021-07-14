from django.forms import (
    Form,
    CharField,
    ChoiceField,
    PasswordInput,
    TextInput,
    EmailInput,
    NumberInput,
    IntegerField,
    RadioSelect,
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
        widget=TextInput(
            attrs={
                'class': 'form-control',
                'ng-model': 'panelName',
                'ng-change': 'checkPanelName()',
                'datangshow': "formPhase=='panelName'",
                'data-min-size': 3
            }
        ),
        label='Name your panel',
        required=True
    )

    panel_type = ChoiceField(
        choices=[
            ('byInvite', 'Private'),
            ('open', 'Public')
        ],
        widget=RadioSelect(
            attrs={
                'ng-model': "panelType",
                'datangshow': "formPhase=='panelType'",
            }
        ),
        help_text='''
        Select private if you only want people with a special link to join. Otherwise, anyone looking for a draft
        can join
        ''',
        required=True
    )

    participant_limit = IntegerField(
        widget=NumberInput(
            attrs={
                'class': 'form-control',
                'ng-model': 'particintLimit',
                'datangshow': "formPhase=='particintLimit'",
                'min': 2
            }
        ),
        label='Participant limit',
        help_text='The maximum number of people who can join your Fantasy Drag Panel',
        required=True
    )

    wildcard_allowance = IntegerField(
        widget=NumberInput(
            attrs={
                'class': 'form-control',
                'ng-model': 'wildcardAllowance',
                'datangshow': "formPhase=='wildcardAllowance'",
                'min': 0,
            }
        ),
        help_text='The number of Wildqueens each player can draft, if any',
        label='Wildqueen allowance',
        required=True
    )
