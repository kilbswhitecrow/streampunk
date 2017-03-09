# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-09 16:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mimo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.Container'),
        ),
        migrations.AlterField(
            model_name='liveitem',
            name='mi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.MoveInItem'),
        ),
        migrations.AlterField(
            model_name='moveinitem',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.PlanItem'),
        ),
        migrations.AlterField(
            model_name='moveoutitem',
            name='live',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.LiveItem'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.Container'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='streampunk.Room'),
        ),
        migrations.AlterField(
            model_name='techitem',
            name='container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.Container'),
        ),
        migrations.AlterField(
            model_name='techitem',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.TechGroup'),
        ),
        migrations.AlterField(
            model_name='techitem',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='streampunk.Room'),
        ),
    ]
