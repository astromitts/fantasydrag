# Generated by Django 3.2.4 on 2021-06-27 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0016_wildcardappearance'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='queen',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='rule',
            options={'ordering': ('score_type', 'point_value', 'name')},
        ),
        migrations.AddField(
            model_name='rule',
            name='score_type',
            field=models.CharField(choices=[('episode', 'episode'), ('season', 'season')], default='episode', max_length=10),
            preserve_default=False,
        ),
    ]
