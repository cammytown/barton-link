# Generated by Django 4.2.4 on 2023-08-11 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excerpts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('progress', models.IntegerField(default=0)),
                ('subprogress', models.IntegerField(default=0)),
            ],
        ),
    ]