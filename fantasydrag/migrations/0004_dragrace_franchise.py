# Generated by Django 3.2.4 on 2021-06-24 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0003_alter_participant_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='dragrace',
            name='franchise',
            field=models.CharField(choices=[('US', 'US'), ('Down Under', 'Down Under'), ('UK', 'UK'), ('Canada', 'Canada')], default='US', max_length=100),
        ),
    ]
