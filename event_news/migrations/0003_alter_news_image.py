# Generated by Django 5.1 on 2025-05-28 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_news', '0002_news_is_public_news_target_faculties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='news_images/'),
        ),
    ]
