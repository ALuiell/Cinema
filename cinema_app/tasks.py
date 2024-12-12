from datetime import timedelta
from django.utils.timezone import now
from cinema_app.models import Order, Ticket
# from background_task import background

# @background(schedule=timedelta(minutes=1)) # background_tasks


def cancel_unpaid_orders():
    expiration_time = timedelta(minutes=15)
    current_time = now()

    unpaid_orders = Order.objects.filter(
        status=Order.PENDING,
        created_at__lte=current_time - expiration_time
    ).prefetch_related('tickets')

    canceled_count = 0

    for order in unpaid_orders:
        order.tickets.update(status=Ticket.CANCELLED)
        order.status = Order.CANCELLED
        order.save()
        canceled_count += 1

    return f"{canceled_count} orders canceled."
