# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('mobileNo', models.CharField(max_length=13)),
                ('emailID', models.EmailField(max_length=75)),
                ('college', models.CharField(max_length=100)),
                ('address', models.ForeignKey(to='address.Address')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
