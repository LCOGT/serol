# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-07 11:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0017_auto_20180216_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='default_proposal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='status.Proposal'),
        ),
    ]