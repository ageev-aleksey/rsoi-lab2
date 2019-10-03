# Generated by Django 2.2.5 on 2019-10-03 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('permission', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nick', models.CharField(max_length=30)),
                ('fname', models.CharField(max_length=30)),
                ('lname', models.CharField(max_length=30)),
                ('patronymic', models.CharField(max_length=30)),
                ('birthday', models.DateField()),
                ('date_registration', models.DateField()),
                ('data_visit', models.DateField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Group')),
            ],
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=50, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.User')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceObject',
            fields=[
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='system.Service')),
                ('object_type', models.CharField(max_length=50)),
            ],
            options={
                'unique_together': {('service', 'object_type')},
            },
        ),
        migrations.CreateModel(
            name='GroupPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Group')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Permission')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.ServiceObject')),
            ],
            options={
                'unique_together': {('group', 'permission', 'object')},
            },
        ),
    ]
