# Generated by Django 4.2.11 on 2024-09-06 00:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_alter_episode_audiofile_alter_show_show_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dj',
            name='profile_theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.theme'),
        ),
    ]
