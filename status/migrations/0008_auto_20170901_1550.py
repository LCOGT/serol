# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-01 15:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0007_auto_20170901_1546'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='answer',
            new_name='text',
        ),
    ]
