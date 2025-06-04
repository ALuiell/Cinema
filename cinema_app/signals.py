from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Order, Ticket



@receiver([post_save, post_delete], sender=Ticket)
def update_order_total_price(sender, instance, **kwargs):
    order = instance.order
    order.total_price = sum(ticket.price for ticket in order.tickets.all())
    order.save()


@receiver(pre_save, sender=Order)
def auto_cancel_tickets(sender, instance, **kwargs):
    if not instance.pk:
        return
    old = Order.objects.get(pk=instance.pk)
    if old.status != Order.CANCELLED and instance.status == Order.CANCELLED:
        instance.tickets.update(status=Ticket.CANCELLED)
