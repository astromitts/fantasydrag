# Generated by Django 3.2.4 on 2021-06-26 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0015_wildcardqueen'),
    ]

    operations = [
        migrations.CreateModel(
            name='WildCardAppearance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.episode')),
                ('queen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.queen')),
            ],
        ),
    ]