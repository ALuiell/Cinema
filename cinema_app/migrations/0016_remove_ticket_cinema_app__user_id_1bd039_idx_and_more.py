# Generated by Django 5.1.2 on 2024-10-28 23:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0015_session_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='ticket',
            name='cinema_app__user_id_1bd039_idx',
        ),
        migrations.RenameField(
            model_name='ticket',
            old_name='users',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='hall',
            name='capacity',
            field=models.PositiveIntegerField(verbose_name='Кількість місць'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['user'], name='cinema_app__user_id_1bd039_idx'),
        ),
    ]