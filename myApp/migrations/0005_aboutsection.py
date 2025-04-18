# Generated by Django 5.1.2 on 2025-03-22 03:38

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0004_category_is_main_header_category_show_on_homepage_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField()),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('is_reversed', models.BooleanField(default=False, help_text='✅ Reverse the row for image on right, text on left')),
                ('order', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
