# Generated by Django 2.0.7 on 2018-08-02 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0021_delete_factcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fact',
            name='published',
            field=models.BooleanField(default=True),
        ),
    ]
