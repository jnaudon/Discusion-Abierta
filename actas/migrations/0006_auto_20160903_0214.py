# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-03 05:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actas', '0005_auto_20160903_0114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemtema',
            old_name='tema_id',
            new_name='tema',
        ),
    ]
