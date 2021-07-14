# Generated by Django 3.2.4 on 2021-07-13 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0044_panel_participant_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel',
            name='panel_type',
            field=models.CharField(choices=[('byInvite', 'Invitation Only'), ('open', 'Open to All')], default='byInvite', max_length=25),
            preserve_default=False,
        ),
    ]
