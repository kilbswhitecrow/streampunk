# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-10 17:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mimo', '0002_auto_20170309_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.TechGroup'),
        ),
        migrations.AddField(
            model_name='settings',
            name='kind',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.TechKind'),
        ),
        migrations.AddField(
            model_name='settings',
            name='subkind',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.TechSubkind'),
        ),
        migrations.AddField(
            model_name='settings',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.Supplier'),
        ),
    ]