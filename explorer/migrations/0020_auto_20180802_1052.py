# Generated by Django 2.0.7 on 2018-08-02 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0019_auto_20180802_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fact',
            name='category',
            field=models.CharField(choices=[('En', 'Engineering'), ('HU', 'Humour'), ('AS', 'Astronomy'), ('OP', 'Operations')], default='AS', max_length=2),
        ),
    ]