import json
from .models import *


def purchase_ticket_process(request, session):
    selected_seats = request.POST.get('selected_seats')
    if not selected_seats:
        return False, "Не вибрано місце"

    try:
        selected_seats = json.loads(selected_seats)
        price = session.base_ticket_price
        tickets = []

        existing_tickets = Ticket.objects.filter(session=session, user=request.user).values_list('seat_number',
                                                                                                 flat=True)

        for seat in selected_seats:
            seat = int(seat)
            if seat in existing_tickets:
                return False, f"Місця зайняті"

            ticket = Ticket.objects.create(session=session, user=request.user, seat_number=seat, price=price)
            tickets.append(ticket)

        ticket_ids = [ticket.id for ticket in tickets]
        request.POST = request.POST.copy()
        return True, {'session_id': session.id, 'ticket_ids': json.dumps(ticket_ids)}

    except ValueError:
        return False, "Неправильний номер місця"
    except Exception as e:
        return False, f"Сталася помилка при створенні квитка: {str(e)}"
