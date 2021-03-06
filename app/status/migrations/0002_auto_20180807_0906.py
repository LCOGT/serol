# Generated by Django 2.0.7 on 2018-08-07 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0001_squashed_0019_auto_20180716_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='image_file',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='progress',
            name='image_status',
            field=models.SmallIntegerField(choices=[(0, 'No Image'), (1, 'Quicklook'), (2, 'Final'), (3, 'Poor Quality')], default=0),
        ),
    ]
