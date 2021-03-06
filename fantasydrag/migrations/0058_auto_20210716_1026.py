# Generated by Django 3.2.4 on 2021-07-16 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0057_populate_rules_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='queen',
            name='tier_score',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='queen',
            name='main_franchise',
            field=models.CharField(choices=[('US', 'US'), ('Australia', 'Down Under'), ('UK', 'UK'), ('Canada', 'Canada')], default='US', max_length=100),
        ),
    ]
