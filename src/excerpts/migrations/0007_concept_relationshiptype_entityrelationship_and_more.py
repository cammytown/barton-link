# Generated by Django 4.2.19 on 2025-02-23 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('excerpts', '0006_rename_character_entity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='RelationshipType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EntityRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('entity_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entity_a', to='excerpts.entity')),
                ('entity_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entity_b', to='excerpts.entity')),
                ('relationship_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='excerpts.relationshiptype')),
            ],
        ),
        migrations.AddField(
            model_name='entity',
            name='relationships',
            field=models.ManyToManyField(related_name='related_entities', through='excerpts.EntityRelationship', to='excerpts.entity'),
        ),
    ]
