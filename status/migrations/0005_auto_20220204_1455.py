# Generated by Django 2.1.7 on 2022-02-04 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0004_auto_20190415_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='requestid',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
    ]
