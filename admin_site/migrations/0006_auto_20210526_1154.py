# Generated by Django 3.2.3 on 2021-05-26 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site', '0005_rename_daily_reports_count_info_id_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firstyear',
            name='branch',
            field=models.CharField(default='null', max_length=30),
        ),
        migrations.AlterField(
            model_name='fourthyear',
            name='branch',
            field=models.CharField(default='null', max_length=30),
        ),
        migrations.AlterField(
            model_name='secondyear',
            name='branch',
            field=models.CharField(default='null', max_length=30),
        ),
        migrations.AlterField(
            model_name='thirdyear',
            name='branch',
            field=models.CharField(default='null', max_length=30),
        ),
    ]
