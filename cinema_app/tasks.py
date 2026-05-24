import logging
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

from cinema_app.models import Order, Ticket

try:
    from celery import shared_task
except ImportError:  # pragma: no cover - optional dependency for local study setup
    def shared_task(*decorator_args, **decorator_kwargs):
        def decorator(func):
            return func

        if decorator_args and callable(decorator_args[0]) and not decorator_kwargs:
            return decorator_args[0]
        return decorator

LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / 'celery_tasks.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


def cancel_unpaid_orders_logic(expiration_minutes=15):
    """Cancel pending orders that are older than the given threshold."""
    try:
        expiration_time = timedelta(minutes=expiration_minutes)
        current_time = now()

        unpaid_orders = Order.objects.filter(
            status=Order.PENDING,
            created_at__lte=current_time - expiration_time
        ).prefetch_related('tickets')

        canceled_count = 0

        for order in unpaid_orders:
            order.tickets.update(status=Ticket.CANCELLED)
            order.status = Order.CANCELLED
            order.save(update_fields=['status', 'updated_at'])
            canceled_count += 1

        logger.info(
            "Canceled %s unpaid orders. Order IDs: %s",
            canceled_count,
            [order.id for order in unpaid_orders],
        )
        return canceled_count
    except Exception:
        logger.exception("Error in cancel_unpaid_orders")
        raise


@shared_task(name='cinema_app.tasks.cancel_unpaid_orders')
def cancel_unpaid_orders():
    return cancel_unpaid_orders_logic()


@shared_task
def send_link_code_email(to_email: str, code: str):
    subject = "Your telegram link code"
    message = f"Enter this code in bot for linked account: {code}"
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
