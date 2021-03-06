# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-07 02:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sfs_site', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='icon',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page',
            name='order',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='page',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sfs_site.Page'),
        ),
    ]
