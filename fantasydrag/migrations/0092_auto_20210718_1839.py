# Generated by Django 3.2.5 on 2021-07-18 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0091_auto_20210718_1227'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_stat', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('stat_type', models.CharField(choices=[('cummulative_dragrace_drafts', 'cummulative_dragrace_drafts'), ('dragrace_rank', 'dragrace_rank'), ('dragrace_panel_scores', 'dragrace_panel_scores')], db_index=True, max_length=100)),
                ('data', models.JSONField(default=dict)),
                ('drag_race', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='fantasydrag.dragrace')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.participant')),
            ],
        ),
        migrations.DeleteModel(
            name='ParticipantStats',
        ),
    ]