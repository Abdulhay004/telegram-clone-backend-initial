# Generated by Django 4.2.16 on 2025-01-20 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0007_alter_groupmessage_options_alter_groupmessage_sender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppermission',
            name='can_send_media',
            field=models.BooleanField(default=True),
        ),
    ]
