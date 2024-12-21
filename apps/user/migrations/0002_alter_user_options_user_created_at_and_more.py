# Generated by Django 4.2.16 on 2024-12-19 10:06

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-created_at'], 'permissions': [('can_send_message', 'Can send messages'), ('can_create_group', 'Can create groups'), ('can_add_contact', 'Can add contacts')], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.HashIndex(fields=['first_name'], name='user_first_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.HashIndex(fields=['last_name'], name='user_last_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['phone_number'], name='user_phone_number_idx'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(('phone_number', None), _negated=True), name='check_phone_number'),
        ),
        migrations.AlterModelTable(
            name='user',
            table='user',
        ),
    ]