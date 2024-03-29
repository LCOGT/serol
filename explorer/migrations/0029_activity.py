# Generated by Django 2.1.7 on 2022-02-07 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0028_auto_20220202_1005'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('desc', models.TextField()),
                ('active', models.BooleanField()),
            ],
        ),
    ]
