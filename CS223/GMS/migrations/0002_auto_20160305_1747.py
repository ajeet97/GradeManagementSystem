# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-05 12:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GMS', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='firstName',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='lastName',
        ),
    ]