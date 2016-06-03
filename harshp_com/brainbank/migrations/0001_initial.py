# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-06 20:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sitebase', '0003_auto_20160214_2024'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrainbankIdea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('slug', models.CharField(db_index=True, max_length=256)),
                ('short_description', models.CharField(max_length=150)),
                ('body_type', models.CharField(choices=[('default', 'textarea'), ('html', 'html'), ('markdown', 'markdown')], db_index=True, default='markdown', max_length=8)),
                ('body', models.TextField()),
                ('body_text', models.TextField(blank=True)),
                ('repo', models.URLField(blank=True, db_index=True, max_length=512, null=True)),
            ],
            options={
                'verbose_name_plural': 'BrainBank Ideas',
                'verbose_name': 'BrainBank idea',
                'ordering': ['title', 'slug'],
            },
        ),
        migrations.CreateModel(
            name='BrainbankPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=128)),
                ('date_created', models.DateTimeField()),
                ('date_published', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('is_published', models.BooleanField(db_index=True, default=False, verbose_name='published')),
                ('short_description', models.CharField(max_length=150)),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
                ('body_type', models.CharField(choices=[('default', 'textarea'), ('html', 'html'), ('markdown', 'markdown')], default='markdown', max_length=8)),
                ('body_text', models.TextField(blank=True)),
                ('body', models.TextField()),
                ('headerimage', models.URLField(blank=True, max_length=256, null=True)),
                ('highlight', models.BooleanField(db_index=True, default=False)),
                ('deliverable', models.BooleanField(db_index=True, default=False)),
                ('authors', models.ManyToManyField(to='sitebase.Author')),
                ('idea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='brainbank.BrainbankIdea')),
                ('tags', models.ManyToManyField(to='sitebase.Tag')),
            ],
            options={
                'verbose_name_plural': 'BrainBank Idea Posts',
                'verbose_name': 'BrainBank Idea Post',
            },
        ),
    ]
