# Generated by Django 5.1.2 on 2024-10-14 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0005_movie_poster'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='age_limit',
            field=models.PositiveIntegerField(choices=[(0, 'Для всіх'), (6, '6+'), (12, '12+'), (16, '16+'), (18, '18+')], default=0, verbose_name='Вікове обмеження'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='movie',
            name='duration',
            field=models.PositiveIntegerField(verbose_name='Тривалість (хвилини)'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='release_date',
            field=models.DateField(verbose_name='Дата випуску'),
        ),
    ]