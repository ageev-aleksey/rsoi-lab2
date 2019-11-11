# Generated by Django 2.2.5 on 2019-11-10 11:00

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileContainer',
            fields=[
                ('name', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='users_files/')),
            ],
        ),
        migrations.CreateModel(
            name='FileInfo',
            fields=[
                ('file_name', models.CharField(max_length=50)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('user', models.UUIDField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.FileContainer')),
            ],
        ),
    ]
