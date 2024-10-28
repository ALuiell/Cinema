from django import template
from ..utils import calculate_dynamic_price

register = template.Library()


@register.filter
def calculate_price(seat_number, base_price, hall_capacity):
    return calculate_dynamic_price(seat_number, base_price, hall_capacity)