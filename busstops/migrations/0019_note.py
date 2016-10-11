# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-09 22:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busstops', '0018_auto_20160911_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('operators', models.ManyToManyField(blank=True, to='busstops.Operator')),
                ('services', models.ManyToManyField(blank=True, to='busstops.Service')),
            ],
        ),
    ]