# Generated by Django 5.1.2 on 2024-10-13 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='description',
            field=models.TextField(default='Немає опису', verbose_name='Опис'),
        ),
    ]
