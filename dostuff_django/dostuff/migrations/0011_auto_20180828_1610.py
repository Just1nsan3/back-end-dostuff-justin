# Generated by Django 2.1 on 2018-08-28 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dostuff', '0010_auto_20180828_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='latitude',
            field=models.FloatField(default=41.881832),
        ),
        migrations.AlterField(
            model_name='event',
            name='longitude',
            field=models.FloatField(default=-87.623177),
        ),
    ]