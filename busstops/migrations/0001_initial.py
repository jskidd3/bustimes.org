# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 18:21
from __future__ import unicode_literals

import busstops.models
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminArea',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('atco_code', models.PositiveIntegerField()),
                ('name', models.CharField(db_index=True, max_length=48)),
                ('short_name', models.CharField(blank=True, max_length=48)),
                ('country', models.CharField(blank=True, max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=48)),
                ('admin_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.AdminArea')),
            ],
        ),
        migrations.CreateModel(
            name='LiveSource',
            fields=[
                ('name', models.CharField(max_length=4, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.CharField(max_length=48, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=48)),
                ('qualifier_name', models.CharField(blank=True, max_length=48)),
                ('latlong', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('adjacent', models.ManyToManyField(blank=True, related_name='neighbour', to='busstops.Locality')),
                ('admin_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.AdminArea')),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='busstops.District')),
                ('parent', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='busstops.Locality')),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('vehicle_mode', models.CharField(blank=True, max_length=48)),
                ('parent', models.CharField(blank=True, max_length=48)),
                ('address', models.CharField(blank=True, max_length=128)),
                ('url', models.URLField(blank=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=128)),
                ('twitter', models.CharField(blank=True, max_length=15)),
            ],
            bases=(busstops.models.ValidateOnSaveMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=48)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('service_code', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('line_name', models.CharField(blank=True, max_length=64)),
                ('line_brand', models.CharField(blank=True, max_length=64)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('outbound_description', models.CharField(blank=True, max_length=255)),
                ('inbound_description', models.CharField(blank=True, max_length=255)),
                ('mode', models.CharField(max_length=11)),
                ('net', models.CharField(blank=True, max_length=3)),
                ('line_ver', models.PositiveIntegerField(blank=True, null=True)),
                ('date', models.DateField()),
                ('current', models.BooleanField(db_index=True, default=True)),
                ('show_timetable', models.BooleanField(default=False)),
                ('geometry', django.contrib.gis.db.models.fields.MultiLineStringField(null=True, srid=4326)),
                ('wheelchair', models.BooleanField(default=False)),
                ('low_floor', models.NullBooleanField()),
                ('assistance_service', models.BooleanField(default=False)),
                ('mobility_scooter', models.BooleanField(default=False)),
                ('operator', models.ManyToManyField(blank=True, to='busstops.Operator')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.Region')),
            ],
        ),
        migrations.CreateModel(
            name='StopArea',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=48)),
                ('stop_area_type', models.CharField(choices=[('GPBS', 'on-street pair'), ('GCLS', 'on-street cluster'), ('GAIR', 'airport building'), ('GBCS', 'bus/coach station'), ('GFTD', 'ferry terminal/dock'), ('GTMU', 'tram/metro station'), ('GRLS', 'rail station'), ('GCCH', 'coach service coverage')], max_length=4)),
                ('latlong', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('active', models.BooleanField()),
                ('admin_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.AdminArea')),
                ('parent', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='busstops.StopArea')),
            ],
        ),
        migrations.CreateModel(
            name='StopPoint',
            fields=[
                ('atco_code', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('naptan_code', models.CharField(db_index=True, max_length=16)),
                ('common_name', models.CharField(db_index=True, max_length=48)),
                ('landmark', models.CharField(blank=True, max_length=48)),
                ('street', models.CharField(blank=True, max_length=48)),
                ('crossing', models.CharField(blank=True, max_length=48)),
                ('indicator', models.CharField(blank=True, max_length=48)),
                ('latlong', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('suburb', models.CharField(blank=True, max_length=48)),
                ('town', models.CharField(blank=True, max_length=48)),
                ('locality_centre', models.BooleanField()),
                ('heading', models.PositiveIntegerField(blank=True, null=True)),
                ('bearing', models.CharField(blank=True, choices=[('N', 'north'), ('NE', 'north east'), ('E', 'east'), ('SE', 'south east'), ('S', 'south'), ('SW', 'south west'), ('W', 'west'), ('NW', 'north west')], max_length=2)),
                ('stop_type', models.CharField(choices=[('AIR', 'Airport entrance'), ('GAT', 'Air airside area'), ('FTD', 'Ferry terminal/dock entrance'), ('FER', 'Ferry/dock berth area'), ('FBT', 'Ferry berth'), ('RSE', 'Rail station entrance'), ('RLY', 'Rail platform access area'), ('RPL', 'Rail platform'), ('TMU', 'Tram/metro/underground entrance'), ('MET', 'MET'), ('PLT', 'Metro and underground platform access area'), ('BCE', 'Bus/coach station entrance'), ('BCS', 'Bus/coach bay/stand/stance within bus/coach station'), ('BCQ', 'Bus/coach bay'), ('BCT', 'On street bus/coach/tram stop'), ('TXR', 'Taxi rank (head of)'), ('STR', 'Shared taxi rank (head of)')], max_length=3)),
                ('bus_stop_type', models.CharField(blank=True, choices=[('MKD', 'Marked (pole, shelter etc)'), ('HAR', 'Hail and ride'), ('CUS', 'Custom (unmarked, or only marked on road)'), ('FLX', 'Flexible zone')], max_length=3)),
                ('timing_status', models.CharField(blank=True, choices=[('PPT', 'Principal point'), ('TIP', 'Time info point'), ('PTP', 'Principal and time info point'), ('OTH', 'Other bus stop')], max_length=3)),
                ('active', models.BooleanField(db_index=True)),
                ('admin_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='busstops.AdminArea')),
                ('live_sources', models.ManyToManyField(blank=True, to='busstops.LiveSource')),
                ('locality', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='busstops.Locality')),
                ('stop_area', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='busstops.StopArea')),
            ],
        ),
        migrations.CreateModel(
            name='StopUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(db_index=True, max_length=8)),
                ('order', models.PositiveIntegerField()),
                ('timing_status', models.CharField(choices=[('PPT', 'Principal point'), ('TIP', 'Time info point'), ('PTP', 'Principal and time info point'), ('OTH', 'Other bus stop')], max_length=3)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.Service')),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.StopPoint')),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='stops',
            field=models.ManyToManyField(editable=False, through='busstops.StopUsage', to='busstops.StopPoint'),
        ),
        migrations.AddField(
            model_name='operator',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.Region'),
        ),
        migrations.AddField(
            model_name='note',
            name='operators',
            field=models.ManyToManyField(blank=True, to='busstops.Operator'),
        ),
        migrations.AddField(
            model_name='note',
            name='services',
            field=models.ManyToManyField(blank=True, to='busstops.Service'),
        ),
        migrations.AddField(
            model_name='adminarea',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.Region'),
        ),
    ]