# Generated by Django 5.1.2 on 2024-12-01 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0021_order_updated_at_ticket_created_at_ticket_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_session_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]
