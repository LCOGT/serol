# Generated by Django 3.2.12 on 2022-02-24 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0007_progress_requestgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='requestid',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]