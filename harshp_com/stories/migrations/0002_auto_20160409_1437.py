# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-09 13:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='highlight',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
