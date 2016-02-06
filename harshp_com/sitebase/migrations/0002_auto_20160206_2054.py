# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-06 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitebase', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='slug',
            field=models.SlugField(default=None, max_length=150, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=150, unique=True),
        ),
    ]
