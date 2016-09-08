# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-08 00:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actas', '0012_auto_20160907_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionencuentro',
            name='max_participantes',
            field=models.IntegerField(default=50),
        ),
        migrations.AddField(
            model_name='configuracionencuentro',
            name='min_participantes',
            field=models.IntegerField(default=7),
        ),
        migrations.AlterField(
            model_name='encuentro',
            name='hash_search',
            field=models.UUIDField(default=b'7bd73040755c11e69e1640e230d28fea'),
        ),
    ]
