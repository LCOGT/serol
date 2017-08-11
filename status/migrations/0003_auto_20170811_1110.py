# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-11 11:10
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0002_auto_20170802_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='status',
            field=django_fsm.FSMField(choices=[('New', 'New'), ('Submitted', 'Submitted'), ('Observed', 'Observed'), ('Failed', 'Failed'), ('Retry', 'Retry'), ('Completed', 'Completed'), ('Identify', 'Identify'), ('Analyse', 'Analyse'), ('Identify', 'Identify'), ('Investigate', 'Investigate')], default='New', max_length=50),
        ),
    ]
