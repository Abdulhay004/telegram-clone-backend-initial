# Generated by Django 4.2.16 on 2025-01-26 07:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0005_alter_groupscheduledmessage_scheduled_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupscheduledmessage',
            name='scheduled_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 27, 7, 46, 53, 105218)),
        ),
    ]
