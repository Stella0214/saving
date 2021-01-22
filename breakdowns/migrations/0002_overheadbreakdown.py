# Generated by Django 3.1.4 on 2021-01-22 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('breakdowns', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverheadBreakdown',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('development_overhead_rate', models.DecimalField(blank=True, decimal_places=2, help_text='Example: Enter 5 for 5% Development_Overhead_Rate', max_digits=6, null=True, verbose_name='Development_Overhead_Rate (%)')),
                ('costbreakdown', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='breakdowns.costbreakdown')),
            ],
            options={
                'verbose_name': '管理费明细',
                'verbose_name_plural': '管理费明细',
                'ordering': ['costbreakdown'],
            },
        ),
    ]
