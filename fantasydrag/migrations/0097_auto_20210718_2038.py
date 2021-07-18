# Generated by Django 3.2.5 on 2021-07-18 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0096_stats_queen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stats',
            name='drag_race',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.dragrace'),
        ),
        migrations.AlterField(
            model_name='stats',
            name='participant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.participant'),
        ),
        migrations.AlterField(
            model_name='stats',
            name='stat_type',
            field=models.CharField(choices=[('cummulative_dragrace_drafts', 'cummulative_dragrace_drafts'), ('dragrace_rank', 'dragrace_rank'), ('dragrace_panel_scores', 'dragrace_panel_scores'), ('dragrace_queen_scores', 'dragrace_queen_scores')], db_index=True, max_length=100),
        ),
    ]
