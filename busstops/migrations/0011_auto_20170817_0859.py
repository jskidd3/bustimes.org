# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-17 07:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busstops', '0010_auto_20170808_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stopusageusage',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
