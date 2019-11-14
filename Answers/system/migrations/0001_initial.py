# Generated by Django 2.2.5 on 2019-11-12 12:41

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
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.UUID, unique=True)),
                ('question_uuid', models.UUIDField()),
                ('text', models.TextField()),
                ('author', models.CharField(max_length=50)),
                ('date', models.DateField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='FilesForAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_uuid', models.UUIDField()),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Answer')),
            ],
            options={
                'unique_together': {('answer', 'file_uuid')},
            },
        ),
    ]
