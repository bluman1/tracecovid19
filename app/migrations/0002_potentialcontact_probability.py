# Generated by Django 2.0 on 2020-03-20 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='potentialcontact',
            name='probability',
            field=models.FloatField(default=0.0),
        ),
    ]
