# Generated by Django 2.1.4 on 2018-12-23 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('busstops', '0034_auto_20180924_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='latest_location',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='latest_vehicle', to='busstops.VehicleLocation'),
        ),
    ]
