# Generated by Django 3.1.4 on 2021-01-23 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breakdowns', '0003_auto_20210123_0710'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='costbreakdown',
            name='profit',
        ),
        migrations.AddField(
            model_name='costbreakdown',
            name='profit_rate',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Example: Enter 5 for 5% Profit_Rate', max_digits=6, null=True, verbose_name='Profit_Rate (%)'),
        ),
    ]
