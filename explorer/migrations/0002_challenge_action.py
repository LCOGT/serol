# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-28 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='action',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
