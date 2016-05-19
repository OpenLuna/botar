# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startTime', models.DateTimeField()),
                ('message', models.TextField(max_length=512)),
                ('sent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FbButton',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('button_type', models.CharField(default=b'postback', max_length=16, choices=[(b'web_url', b'web_url'), (b'postback', b'postback')])),
                ('title', models.CharField(max_length=128)),
                ('url', models.URLField(max_length=128, null=True, blank=True)),
                ('payload', models.CharField(max_length=128, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FbCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, null=True, blank=True)),
                ('subtitle', models.CharField(max_length=128, null=True, blank=True)),
                ('image', models.URLField(max_length=128, null=True, blank=True)),
                ('keyword', models.CharField(max_length=128, null=True, blank=True)),
                ('buttons', models.ManyToManyField(to='bot_content.FbButton', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fb_id', models.CharField(max_length=30)),
                ('reg_feeds', models.ManyToManyField(to='bot_content.Feed')),
            ],
        ),
        migrations.AddField(
            model_name='events',
            name='feed',
            field=models.ForeignKey(to='bot_content.Feed'),
        ),
    ]
