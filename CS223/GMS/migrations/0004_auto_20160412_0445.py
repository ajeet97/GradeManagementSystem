# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-11 23:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GMS', '0003_auto_20160306_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructor',
            name='department',
            field=models.CharField(max_length=30),
        ),
    ]