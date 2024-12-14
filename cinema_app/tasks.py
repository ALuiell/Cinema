import logging
from datetime import timedelta
from django.utils.timezone import now
from cinema_app.models import Order, Ticket
from background_task import background

# Настройка логирования
logging.basicConfig(
    filename='background_tasks.log',  # Имя файла для логов
    level=logging.INFO,               # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщения
)

logger = logging.getLogger(__name__)

@background(schedule=timedelta(hours=1))
def cancel_unpaid_orders():
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
