# Generated by Django 2.1.7 on 2019-09-25 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0023_auto_20190729_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
                ('jsfile', models.CharField(choices=[('halloween.js', 'halloween'), ('asteroid-day.js', 'asteroid day'), ('equinox.js', 'equinox'), ('new-year.js', 'new year'), ('earth-day.js', 'earth day'), ('perseids.js', 'perseids'), ('christmas.js', 'christmas'), ('', '')], max_length=20)),
            ],
        ),
    ]
