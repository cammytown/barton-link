# Generated by Django 4.2.1 on 2023-06-18 00:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('excerpts', '0004_tagtype_tag_tag_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='tag_type',
            new_name='type',
        ),
    ]
