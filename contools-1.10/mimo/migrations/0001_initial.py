# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-09 15:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('streampunk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.Container')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streampunk.Room')),
            ],
        ),
        migrations.CreateModel(
            name='ContainerType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='LiveItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='MoveInItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='MoveOutItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PlanItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('Plan', 'Planning'), ('MI', 'Move In'), ('Live', 'Live event'), ('MO', 'Move Out')], default='Plan', max_length=16)),
                ('container', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.Container')),
                ('room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='streampunk.Room')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='TechGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(blank=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='TechItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=32)),
                ('count', models.IntegerField(default=1)),
                ('state', models.CharField(blank=True, max_length=32)),
                ('container', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.Container')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.TechGroup')),
            ],
        ),
        migrations.CreateModel(
            name='TechKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='TechSubkind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='techitem',
            name='kind',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.TechKind'),
        ),
        migrations.AddField(
            model_name='techitem',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='streampunk.Room'),
        ),
        migrations.AddField(
            model_name='techitem',
            name='subkind',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.TechSubkind'),
        ),
        migrations.AddField(
            model_name='techitem',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.Supplier'),
        ),
        migrations.AddField(
            model_name='planitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.TechItem'),
        ),
        migrations.AddField(
            model_name='moveoutitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.TechItem'),
        ),
        migrations.AddField(
            model_name='moveoutitem',
            name='live',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.LiveItem'),
        ),
        migrations.AddField(
            model_name='moveinitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.TechItem'),
        ),
        migrations.AddField(
            model_name='moveinitem',
            name='plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.PlanItem'),
        ),
        migrations.AddField(
            model_name='liveitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.TechItem'),
        ),
        migrations.AddField(
            model_name='liveitem',
            name='mi',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mimo.MoveInItem'),
        ),
        migrations.AddField(
            model_name='container',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mimo.ContainerType'),
        ),
    ]