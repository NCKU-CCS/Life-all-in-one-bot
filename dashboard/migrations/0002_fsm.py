# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 02:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FSM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fb_id', models.CharField(default='non_data', max_length=320)),
                ('first_name', models.CharField(default='non_data', max_length=320)),
                ('last_name', models.CharField(default='non_data', max_length=320)),
                ('gender', models.BooleanField()),
                ('state', models.IntegerField()),
            ],
        ),
    ]
