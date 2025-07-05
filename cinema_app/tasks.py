import logging
from datetime import timedelta
from django.utils.timezone import now
from celery import shared_task
from cinema_app.models import Order, Ticket

# Настройка логирования
logging.basicConfig(
    filename='logs/celery_tasks.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

@shared_task(name='cinema_app.tasks.cancel_unpaid_orders')
def cancel_unpaid_orders():
    """
    Отменяет неоплаченные заказы через 1 минуту после создания.
    """
    try:
        expiration_time = timedelta(minutes=1)
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

        logger.info(f"Canceled {canceled_count} unpaid orders. Order IDs: {[order.id for order in unpaid_orders]}")

    except Exception as e:
        logger.error(f"Error in cancel_unpaid_orders: {e}")
        raise
