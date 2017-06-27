# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=256)),
                ('seen', models.BooleanField(default=False)),
                ('liked', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Movies',
                'ordering': ['title'],
                'verbose_name': 'Movie',
            },
        ),
        migrations.CreateModel(
            name='MovieList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=256)),
                ('slug', models.SlugField(max_length=256)),
                ('movies', models.ManyToManyField(related_name='lists', to='hobbies.Movie')),
            ],
            options={
                'verbose_name_plural': 'Movie Lists',
                'ordering': ['title'],
                'verbose_name': 'Movie List',
            },
        ),
    ]
