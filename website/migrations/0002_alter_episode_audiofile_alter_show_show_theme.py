# Generated by Django 4.2.11 on 2024-09-06 00:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='audiofile',
            field=models.FileField(blank=True, null=True, upload_to='episodes'),
        ),
        migrations.AlterField(
            model_name='show',
            name='show_theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.theme'),
        ),
    ]
