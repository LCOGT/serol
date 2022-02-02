# Generated by Django 2.1.7 on 2022-02-02 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0026_season_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='icon',
            field=models.CharField(blank=True, choices=[('1.1.1-mars.png', 'Mars'), ('1.1.2-jupiter.png', 'Jupiter'), ('1.1.2-neptune.png', 'Neptune'), ('1.1.2-saturn.png', 'Saturn'), ('1.1.2-uranus.png', 'Uranus'), ('2.2-comet-icon.png', 'Comet'), ('2.3-asteroids-icon.png', 'Asteroid')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='body',
            name='icon',
            field=models.CharField(choices=[('1.1.1-mars.png', 'Mars'), ('1.1.2-jupiter.png', 'Jupiter'), ('1.1.2-neptune.png', 'Neptune'), ('1.1.2-saturn.png', 'Saturn'), ('1.1.2-uranus.png', 'Uranus'), ('2.2-comet-icon.png', 'Comet'), ('2.3-asteroids-icon.png', 'Asteroid')], max_length=20),
        ),
        migrations.AlterField(
            model_name='season',
            name='jsfile',
            field=models.CharField(choices=[('halloween.json', 'halloween'), ('asteroid-day.json', 'asteroid day'), ('equinox2020.json', 'equinox'), ('new-year.json', 'new year'), ('earth-day.json', 'earth day'), ('perseids.json', 'perseids'), ('christmas.json', 'christmas')], max_length=20),
        ),
    ]
