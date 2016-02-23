# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-23 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GMS', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crs1', models.CharField(choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F')], default=b'', max_length=1)),
                ('crs2', models.CharField(choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F')], default=b'', max_length=1)),
                ('crs3', models.CharField(choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F')], default=b'', max_length=1)),
                ('crs4', models.CharField(choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F')], default=b'', max_length=1)),
                ('crs5', models.CharField(choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F')], default=b'', max_length=1)),
                ('crs6', models.CharField(choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F')], default=b'', max_length=1)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='GMS.Student')),
            ],
        ),
    ]