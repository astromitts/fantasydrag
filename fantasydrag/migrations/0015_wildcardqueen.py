# Generated by Django 3.2.4 on 2021-06-26 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0014_auto_20210625_2137'),
    ]

    operations = [
        migrations.CreateModel(
            name='WildCardQueen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('panel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.panel')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.participant')),
                ('queen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.queen')),
            ],
        ),
    ]
