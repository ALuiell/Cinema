from django.utils.text import slugify
from decimal import Decimal


def poster_upload_to(instance, filename):
    slug = slugify(instance.original_name)
    ext = filename.split('.')[-1]
    return f'posters/{slug}.{ext}'


def generate_session_slug(instance):
    film_title_slug = slugify(instance.movie.original_name)
    session_date_str = instance.session_date.strftime('%Y-%m-%d')
    start_time_str = instance.start_time.strftime('%H-%M')
    return f"{film_title_slug}-{session_date_str}-{start_time_str}"


def calculate_dynamic_price(seat_number, base_price, hall_capacity):
    if seat_number is None or base_price is None or hall_capacity is None:
        raise ValueError("seat_number, base_price, and hall_capacity must not be None.")

    total_rows = hall_capacity // 10
    total_seats_in_row = 10
    row = (seat_number - 1) // total_seats_in_row + 1

    if base_price <= 0:
        raise ValueError("Base price must be greater than 0.")

    center_rows = range(total_rows // 2 - 1, total_rows // 2 + 1)
    center_seats = range(total_seats_in_row // 2 - 3, total_seats_in_row // 2 + 4)

    if row in center_rows and seat_number in center_seats:
        return float(base_price * Decimal('1.5'))
    elif row in center_rows:
        return float(base_price * Decimal('1.2'))

    return float(base_price)