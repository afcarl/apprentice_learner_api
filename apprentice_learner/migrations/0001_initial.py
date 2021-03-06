# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-26 16:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActionSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance', picklefield.fields.PickledObjectField(editable=False)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('num_request', models.IntegerField(default=0)),
                ('num_train', models.IntegerField(default=0)),
                ('num_check', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('action_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apprentice_learner.ActionSet')),
            ],
            options={
                'ordering': ('-updated',),
            },
        ),
        migrations.CreateModel(
            name='PyFunction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('fun_def', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='actionset',
            name='features',
            field=models.ManyToManyField(blank=True, related_name='feature_action_sets', to='apprentice_learner.PyFunction'),
        ),
        migrations.AddField(
            model_name='actionset',
            name='functions',
            field=models.ManyToManyField(blank=True, related_name='function_action_sets', to='apprentice_learner.PyFunction'),
        ),
    ]
