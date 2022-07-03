# Generated by Django 4.0.4 on 2022-06-29 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('playlists', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='category',
        ),
        migrations.AddField(
            model_name='playlist',
            name='category',
            field=models.ManyToManyField(blank=True, null=True, related_name='playlists', to='categories.category'),
        ),
    ]