# Generated by Django 3.2.12 on 2022-08-02 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0010_auto_20220629_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='siteid',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
