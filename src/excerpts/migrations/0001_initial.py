# Generated by Django 4.2.1 on 2023-07-01 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Excerpt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('content', models.TextField()),
                ('metadata', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('characters', models.ManyToManyField(to='excerpts.character')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TagType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='excerpts.tagtype')),
            ],
            options={
                'abstract': False,
            },
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
        migrations.CreateModel(
            name='ExcerptTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_autotag', models.BooleanField(default=False)),
                ('excerpt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='excerpts.excerpt')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='excerpts.tag')),
            ],
        ),
        migrations.CreateModel(
            name='ExcerptSimilarity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sbert_similarity', models.FloatField()),
                ('excerpt1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='excerpt1', to='excerpts.excerpt')),
                ('excerpt2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='excerpt2', to='excerpts.excerpt')),
            ],
        ),
        migrations.CreateModel(
            name='ExcerptRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child', to='excerpts.excerpt')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='excerpts.excerpt')),
            ],
        ),
        migrations.AddField(
            model_name='excerpt',
            name='parents',
            field=models.ManyToManyField(related_name='children', through='excerpts.ExcerptRelationship', to='excerpts.excerpt'),
        ),
        migrations.AddField(
            model_name='excerpt',
            name='tags',
            field=models.ManyToManyField(related_name='excerpts', through='excerpts.ExcerptTag', to='excerpts.tag'),
        ),
        migrations.AddField(
            model_name='character',
            name='tags',
            field=models.ManyToManyField(to='excerpts.tag'),
        ),
    ]
