# Generated by Django 4.2.11 on 2024-09-06 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_alter_episode_name_alter_show_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dj',
            name='bio',
            field=models.TextField(default='working on something big'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='description',
            field=models.TextField(default='my new episode'),
        ),
        migrations.AlterField(
            model_name='show',
            name='description',
            field=models.TextField(default='my new show'),
        ),
    ]