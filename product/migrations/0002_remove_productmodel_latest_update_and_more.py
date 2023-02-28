# Generated by Django 4.1.7 on 2023-02-22 07:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productmodel',
            name='latest_update',
        ),
        migrations.AddField(
            model_name='productmodel',
            name='latest_updated',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Последнее обновление'),
        ),
    ]