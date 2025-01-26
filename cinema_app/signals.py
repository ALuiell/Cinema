from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, Ticket



@receiver([post_save, post_delete], sender=Ticket)
def update_order_total_price(sender, instance, **kwargs):
    order = instance.order
    order.total_price = sum(ticket.price for ticket in order.tickets.all())
    order.save()

