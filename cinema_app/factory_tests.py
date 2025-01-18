import random
import factory
from cinema_app.models import *
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")  # default password = 'password123'

class HallFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hall

    name = factory.Faker("name")
    capacity = factory.Faker("random_int", min=40, max=100)


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Faker("word")



class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie

    title = factory.Faker("name")
    original_name = factory.Faker("name")
    description = factory.Faker("paragraph")
    release_date = factory.LazyFunction(
        lambda: datetime.now().date() + timedelta(days=random.randint(1, 5 * 365))
    )
    duration = 120
    age_limit = 12


class SessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Session

    hall = factory.SubFactory(HallFactory)
    movie = factory.SubFactory(MovieFactory)
    base_ticket_price = 100
    session_date = factory.LazyFunction(
        lambda: datetime.now().date() + timedelta(days=random.randint(1, 10))
    )
    start_time = factory.LazyFunction(
        lambda: (datetime.combine(datetime.today(), time(10, 0)) +
                 timedelta(minutes=random.randint(0, 13 * 60 - 1))).time()
    )


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    session = factory.SubFactory(SessionFactory)
    status = Order.PENDING
    total_price = factory.LazyAttribute(lambda obj: obj.session.base_ticket_price * obj.tickets.count())


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    session = factory.LazyAttribute(
        lambda obj: obj.order.session
    )
    price = factory.LazyAttribute(lambda obj: obj.session.base_ticket_price)
    seat_number = factory.LazyAttribute(
        lambda obj: random.choice(obj.session.get_available_seats())
    )
    order = factory.SubFactory(OrderFactory)
    status = Ticket.RESERVED
    user = factory.LazyAttribute(
        lambda obj: obj.order.user
    )


