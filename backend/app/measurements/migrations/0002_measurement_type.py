# Generated by Django 3.0.7 on 2020-06-25 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='type',
            field=models.IntegerField(default=1),
        ),
    ]
