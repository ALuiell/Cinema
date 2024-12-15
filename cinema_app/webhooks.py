import stripe
from django.conf import settings
from django.http import HttpResponse
from .models import Order, Ticket
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('client_reference_id')
        try:
            order = Order.objects.get(id=order_id)
            if session['payment_status'] == 'paid':
                order.status = Order.COMPLETED
                order.save()
                tickets = Ticket.objects.filter(order=order)
                for ticket in tickets:
                    ticket.status = Ticket.BOOKED
                tickets.bulk_update(tickets, ['status'])
        except Order.DoesNotExist:
            logger.warning(f"Order with ID {order_id} not found during webhook processing.")
            return HttpResponse(status=400)

    return HttpResponse(status=200)
