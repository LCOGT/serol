# Generated by Django 2.1.7 on 2019-09-26 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0025_auto_20190925_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='message',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
