# Generated by Django 4.2.1 on 2023-06-13 20:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('excerpts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='excerpt',
            old_name='excerpt',
            new_name='content',
        ),
        migrations.CreateModel(
            name='ExcerptVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('excerpt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='excerpts.excerpt')),
            ],
        ),
    ]
