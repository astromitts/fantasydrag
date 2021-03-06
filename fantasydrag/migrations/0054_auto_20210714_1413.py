# Generated by Django 3.2.4 on 2021-07-14 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0053_remove_panel_draft_rules'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='panel',
            name='draft_type',
        ),
        migrations.AlterField(
            model_name='panel',
            name='current_participant',
            field=models.IntegerField(default=0, help_text='PK of participant whos turn it is right now in the draft'),
        ),
        migrations.AlterField(
            model_name='panel',
            name='draft_order',
            field=models.JSONField(blank=True, default=list, help_text='A random order list (0-participants.count) for draft selection. Abstracted from participant IDs.', null=True),
        ),
        migrations.AlterField(
            model_name='panel',
            name='draft_rounds',
            field=models.JSONField(blank=True, default=dict, help_text='A dictionary detailing which ordered participants get to select in each draft. Populated by utils.calculate_draft_data.', null=True),
        ),
        migrations.AlterField(
            model_name='panel',
            name='total_drafts',
            field=models.IntegerField(default=0, help_text='Total number of draft rounds that there will be in the main draft. Populated by utils.calculate_draft_data.'),
        ),
    ]
