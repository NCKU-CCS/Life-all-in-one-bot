# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-08 09:16
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20161208_0902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fsm',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=None, geography=True, srid=4326),
        ),
    ]
