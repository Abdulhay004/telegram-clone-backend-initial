# Generated by Django 4.2.16 on 2025-01-26 15:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channelscheduledmessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channelmessage',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='channel.channel'),
        ),
        migrations.AddField(
            model_name='channelmessage',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_channel_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channelmessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channelmembership',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='channel.channel'),
        ),
        migrations.AddField(
            model_name='channelmembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channel',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='channelmembership',
            unique_together={('channel', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='channel',
            unique_together={('name', 'owner')},
        ),
    ]
