# Generated by Django 2.0.6 on 2018-07-10 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busstops', '0028_auto_20180610_2100'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vehicletype',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='service',
            name='timetable_wrong',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehiclelocation',
            name='early',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclelocation',
            name='heading',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='operator',
            name='twitter',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
