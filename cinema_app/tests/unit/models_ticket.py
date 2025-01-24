import time
from django.test import TestCase
from django.core.exceptions import ValidationError
from cinema_app.tests.factory_tests import TicketFactory, UserFactory, GenreFactory, MovieFactory, SessionFactory
from cinema_app.models import Ticket


#REWORK
class TicketModelTestCase(TestCase):

    def setUp(self):
        """Sets up initial test data for the Ticket model."""
        self.ticket = TicketFactory(seat_number=10)
        self.ticket2 = TicketFactory(session=self.ticket.session)

    def test_ticket_creation(self):
        """Test successful creation of a Session."""
        self.assertIsNotNone(self.ticket.session)
        self.assertIsNotNone(self.ticket.session.hall)
        self.assertIsNotNone(self.ticket.session.movie)

        self.assertIsNotNone(self.ticket.order)
        self.assertIsNotNone(self.ticket.order.user)

        self.assertIsNotNone(self.ticket.price)
        self.assertIsNotNone(self.ticket.status)

        self.assertEqual(self.ticket.session, self.ticket2.session)
        self.assertNotIn(self.ticket.seat_number, self.ticket.session.get_available_seats())

    def test_ticket_str_method(self):
        """Test the string representation of the Ticket model."""
        ticket = TicketFactory()
        self.assertEqual(str(ticket), f"{ticket.order.user.first_name} {ticket.order.user.last_name} | {ticket.session.movie} | {ticket.session}")

    def test_unique_constraint_model_level(self):
        """Test unique constraint for session and seat_number at the model level."""
        # added validator to models  # Restricted by unique constraint
        with self.assertRaises(ValidationError):
            TicketFactory(
                    session=self.ticket.session,
                    seat_number=self.ticket.seat_number
                )

    def test_ticket_status_valid_choices(self):
        """Test that a Ticket can only have a valid status."""
        for valid_status in ['reserved', 'booked', 'cancelled']:
            try:
                ticket = TicketFactory(status=valid_status)
                self.assertEqual(ticket.status, valid_status)
            except ValidationError:
                self.fail(f"ValidationError raised for valid status: {valid_status}")

    def test_ticket_invalid_status(self):
        """Test that an invalid status raises a ValidationError."""
        with self.assertRaises(ValidationError):
            TicketFactory(
                status="invalid status"
            )

    # 2. Проверка цены билета
    def test_ticket_price_from_session(self):
        """Test that the ticket price matches the session's base_ticket_price."""
        ticket = TicketFactory()
        self.assertTrue(ticket.price == ticket.session.base_ticket_price)

    def test_ticket_negative_price(self):
        """Test that a negative or zero price raises a ValidationError."""
        with self.assertRaises(ValidationError):
            TicketFactory(
                price=0
            )

        with self.assertRaises(ValidationError):
            TicketFactory(
                price=-10
            )

    def test_ticket_user_association(self):
        """Test that a Ticket must be associated with a User."""
        ticket = TicketFactory()
        self.assertEqual(ticket.user_id, ticket.order.user.id)


    def test_ticket_without_user(self):
        """Test that creating a Ticket without a user raises a ValidationError."""
        ticket = TicketFactory.build(user=None, session=self.ticket.session)
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    # 4. Проверка привязки к заказу
    def test_ticket_order_association(self):
        """Test that a Ticket must be associated with an Order."""
        ticket = TicketFactory()
        self.assertIsNotNone(ticket.order)


    def test_ticket_without_order(self):
        """Test that creating a Ticket without an order raises a ValidationError."""
        ticket = TicketFactory.build(session=self.ticket.session, order=None, user=UserFactory())
        with self.assertRaises(ValidationError):
            ticket.full_clean()


    # 5. Доступность мест
    def test_seat_availability_after_ticket_creation(self):
        """Test that a seat becomes unavailable after a Ticket is created."""
        ticket = TicketFactory(seat_number=1)
        self.assertNotIn(ticket.seat_number, ticket.session.get_available_seats())

    def test_ticket_for_occupied_seat(self):
        """Test that a Ticket cannot be created for an already occupied seat."""
        ticket = TicketFactory(seat_number=1)
        with self.assertRaises(ValidationError):
            TicketFactory(
                session=ticket.session,
                seat_number=ticket.seat_number
            )

    # 6. Проверка времени создания
    def test_ticket_created_at_auto_set(self):
        """Test that created_at is automatically set when a Ticket is created."""
        ticket = TicketFactory()
        self.assertIsNotNone(ticket.created_at)

    def test_ticket_updated_at_auto_update(self):
        """Test that updated_at is updated when a Ticket is modified."""

        ticket = TicketFactory()
        og_updated_at = ticket.updated_at
        time.sleep(1)

        new_seat_number = ticket.session.get_available_seats()[0]
        ticket.seat_number = new_seat_number

        ticket.save()
        self.assertNotEqual(og_updated_at, ticket.updated_at)


    # 7. Проверка метода clean
    def test_seat_number_within_capacity(self):
        """Test that the seat_number is within the hall's capacity."""
        ticket = TicketFactory()
        hall = ticket.session.hall
        max_capacity = hall.capacity
        self.assertTrue(1 <= ticket.seat_number <= max_capacity)

    # 8. Тесты Many-to-One и Foreign Key
    def test_ticket_deleted_with_session(self):
        """Test that deleting a session deletes all related Tickets."""
        ticket = TicketFactory()
        session_id = ticket.session.id  # Store the session's ID before deletion
        ticket.session.delete()  # Delete the session
        self.assertFalse(Ticket.objects.filter(session_id=session_id).exists())

    def test_ticket_deleted_with_order(self):
        """Test that deleting an order deletes all related Tickets."""
        ticket = TicketFactory()
        order_id = ticket.order.id
        ticket.order.delete()
        self.assertFalse(Ticket.objects.filter(order=order_id).exists())


    def test_ticket_min_seat_number(self):
        """Test that a Ticket can be created with the minimum seat number (e.g., 1)."""
        ticket = TicketFactory(seat_number=1)
        self.assertEqual(ticket.seat_number, 1)


    # 10. Логика отмены билета
    def test_ticket_status_cancelled_frees_seat(self):
        """Test that changing the status to CANCELLED makes the seat available again."""
        ticket = TicketFactory(status='cancelled')
        self.assertIn(ticket.seat_number, ticket.session.get_available_seats())

    def test_get_available_seats_after_ticket_creation(self):
        """Test that `get_available_seats` correctly excludes occupied seats."""
        ticket = TicketFactory(seat_number=1)
        ticket2 = TicketFactory(seat_number=2)
        ticket3 = TicketFactory(seat_number=3)
        for ticket in [ticket, ticket2, ticket3]:
            self.assertNotIn(ticket.seat_number, ticket.session.get_available_seats())

    def test_get_available_seats_after_ticket_deletion(self):
        """Test that `get_available_seats` includes a seat after the Ticket is deleted."""
        ticket = TicketFactory(seat_number=1)
        self.assertNotIn(ticket.seat_number, ticket.session.get_available_seats())
        ticket.delete()
        self.assertIn(ticket.seat_number, ticket.session.get_available_seats())


    # 12. Проверка строкового представления
    def test_ticket_str_updated_on_user_change(self):
        """Test that the string representation updates if the User's name changes."""
        ticket = TicketFactory()
        # Store the initial string representation of the ticket.
        initial_str = str(ticket)

        # Change the user's first and last name.
        ticket.user.first_name = "UpdatedFirstName"
        ticket.user.last_name = "UpdatedLastName"
        ticket.user.save()

        # Fetch the updated ticket from the database.
        updated_ticket = Ticket.objects.get(id=ticket.id)

        # Confirm that the updated string representation reflects the changed user name.
        self.assertEqual(
            str(updated_ticket),
            f"{updated_ticket.user.first_name} {updated_ticket.user.last_name} | {updated_ticket.session.movie} | {updated_ticket.session}"
        )
        self.assertNotEqual(initial_str, str(updated_ticket))

    def test_ticket_str_updated_on_movie_change(self):
        """Test that the string representation updates if the movie title changes."""
        self.genre1 = GenreFactory(name="Fantasy")
        self.genre2 = GenreFactory(name="Sci-Fi")
        movie = MovieFactory(genre=[self.genre1, self.genre2])
        session = SessionFactory(movie=movie)
        ticket = TicketFactory(session=session)
        initial_str = str(ticket)

        ticket.session.movie.title = "Updated Movie Title"
        ticket.session.movie.save()

        updated_ticket = Ticket.objects.get(id=ticket.id)

        self.assertEqual(
            str(updated_ticket),
            f"{updated_ticket.user.first_name} {updated_ticket.user.last_name} | {updated_ticket.session.movie} | {updated_ticket.session}"
        )
        self.assertNotEqual(initial_str, str(updated_ticket))