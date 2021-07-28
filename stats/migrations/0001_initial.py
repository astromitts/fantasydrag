# Generated by Django 3.2.5 on 2021-07-26 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fantasydrag', '0100_panel_draft_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueenEpisodeScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.episode')),
                ('queen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.queen')),
                ('viewing_participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewingparticipant_queen_episode_score', to='fantasydrag.participant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QueenDragRaceScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('drag_race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.dragrace')),
                ('queen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.queen')),
                ('viewing_participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewingparticipant_queen_dragrace_score', to='fantasydrag.participant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PanelistEpisodeScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.episode')),
                ('panel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.panel')),
                ('panelist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='targetparticipant_panelist_episode_score', to='fantasydrag.participant')),
                ('viewing_participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewingparticipant_panelist_episode_score', to='fantasydrag.participant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PanelistDragRaceScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('panel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.panel')),
                ('panelist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='targetparticipant_panelist_dragrace_score', to='fantasydrag.participant')),
                ('viewing_participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewingparticipant_panelist_dragrace_score', to='fantasydrag.participant')),
            ],
        ),
    ]