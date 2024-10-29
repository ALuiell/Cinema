# Generated by Django 5.1.2 on 2024-10-18 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0006_movie_age_limit_alter_movie_duration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='seat_number',
            field=models.PositiveIntegerField(default=1, verbose_name='Номер місця'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='hall',
            name='capacity',
            field=models.IntegerField(verbose_name='Кількість місць'),
        ),
        migrations.AlterField(
            model_name='hall',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Зал'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Назва'),
        ),
        migrations.AlterField(
            model_name='session',
            name='end_time',
            field=models.TimeField(verbose_name='Кінець сеансу'),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_date',
            field=models.DateField(verbose_name='Дата сеансу'),
        ),
        migrations.AlterField(
            model_name='session',
            name='start_time',
            field=models.TimeField(verbose_name='Початок сеансу'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ціна'),
        ),
    ]