# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-16 15:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0016_auto_20180216_1515'),
    ]

    operations = [
        migrations.RenameField(
            model_name='progress',
            old_name='tracking_num',
            new_name='requestid',
        ),
        migrations.RemoveField(
            model_name='progress',
            name='userrequestid',
        ),
    ]
