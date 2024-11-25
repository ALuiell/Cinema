import json
from .models import *
from django.db import transaction


def process_payment(user, order, total_price):
    """
    Эмулирует процесс оплаты.
    Возвращает True, если оплата прошла успешно, иначе False.
    """
    # Здесь вы интегрируете реальный платежный API
    # Например, Stripe, PayPal или другой сервис.
    payment_successful = True
    if payment_successful:
        return True
    else:
        return False


def purchase_ticket_process(request, session):
    selected_seats = request.POST.get('selected_seats')
    if not selected_seats:
        return False, "Не вибрано місце"

    try:
        selected_seats = json.loads(selected_seats)
        price = session.base_ticket_price
        total_price = price * len(selected_seats)

        with transaction.atomic():
            order = Order.objects.create(user=request.user, session=session)
            tickets = []

            existing_tickets = set(
                Ticket.objects.filter(session=session).values_list('seat_number', flat=True)
            )

            for seat in selected_seats:
                seat = int(seat)
                if seat in existing_tickets:
                    return False, f"Місце {seat} вже зайняте"

                ticket = Ticket.objects.create(
                    session=session, user=request.user, seat_number=seat, price=price, order=order
                )
                tickets.append(ticket)

            if not process_payment(request.user, order, total_price):
                raise Exception("Оплата не пройшла. Замовлення не створено.")

            # Меняем статус заказа на 'completed'
            order.status = 'completed'
            order.calculate_total_price()
            order.save()

        ticket_ids = [ticket.id for ticket in tickets]
        return True, {'session_id': session.id, 'ticket_ids': json.dumps(ticket_ids)}

    except ValueError:
        return False, "Неправильний номер місця"
    except Exception as e:
        return False, f"Сталася помилка: {str(e)}"
