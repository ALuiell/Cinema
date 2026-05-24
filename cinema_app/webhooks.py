import logging
from pathlib import Path

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse

from .models import Order, Ticket

try:
    import stripe
except ImportError:  # pragma: no cover - optional dependency for local study setup
    stripe = None

if stripe is not None:
    stripe.api_key = settings.STRIPE_SECRET_KEY

LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / 'webhooks.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


@csrf_exempt
def stripe_webhook(request):
    if stripe is None:
        return JsonResponse({'error': 'Stripe library is not installed.'}, status=503)

    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
        return JsonResponse({'error': 'Stripe webhook is not configured.'}, status=503)

    payload = request.body.decode('utf-8')
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # Stripe signature verification
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        logger.info(f"Received event: {event['type']}")
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Event Handling `checkout.session.completed`
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Session data: {session}")

        # Getting order ID
        order_id = session.get('client_reference_id')
        if not order_id:
            logger.error("Missing 'client_reference_id'")
            return JsonResponse({'error': "Missing 'client_reference_id'"}, status=400)

        try:
            # Looking for an order in the database
            order = Order.objects.get(id=order_id)
            logger.info(f"Found order {order.id}")

            # Checking the payment status
            if session.get('payment_status') == 'paid':
                if order.status == Order.PENDING:
                    order.status = Order.COMPLETED
                    order.save()
                    tickets = Ticket.objects.filter(order=order)
                    for ticket in tickets:
                        ticket.status = Ticket.BOOKED
                    tickets.bulk_update(tickets, ['status'])
                    logger.info(f"Order {order.id} marked as COMPLETED")
            else:
                logger.warning(f"Payment not completed for order {order.id}")

        except Order.DoesNotExist:
            logger.error(f"Order with ID {order_id} does not exist")
            return JsonResponse({'error': 'Order not found'}, status=404)

    else:
        # Handling other types of events
        logger.warning(f"Unhandled event type: {event['type']}")

    return JsonResponse({'status': 'success'}, status=200)
