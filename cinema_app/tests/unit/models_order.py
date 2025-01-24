from django.test import TestCase
from django.core.exceptions import ValidationError
from cinema_app.tests.factory_tests import OrderFactory, TicketFactory
from cinema_app.models import Order, Ticket
from django.db.utils import IntegrityError
import time
import random


class OrderModelTestCase(TestCase):
    def setUp(self):
        self.order = OrderFactory()

    def test_order_creation(self):
        """Test that an Order object is created successfully."""
        self.assertIsNotNone(self.order)
        self.assertIsNotNone(self.order.user)
        self.assertIsNotNone(self.order.session)
        self.assertIsNotNone(self.order.status)
        self.assertIsNotNone(self.order.total_price)
        self.assertIsNotNone(self.order.created_at)
        self.assertIsNotNone(self.order.updated_at)

    def test_order_default_status(self):
        """Test that the default status of an Order is 'pending'."""
        order = OrderFactory()
        self.assertEqual(order.status, Order.PENDING)

    def test_order_creation_without_user(self):
        """Test that creating an Order without a user raises a ValidationError."""
        with self.assertRaises(ValidationError):
            order = OrderFactory.build(user=None)
            order.full_clean()

    def test_order_creation_without_session(self):
        """Test that creating an Order without a session raises a ValidationError."""
        with self.assertRaises(ValidationError):
            order = OrderFactory.build(session=None)
            order.full_clean()

    def test_order_status_valid_choices(self):
        """Test that an Order can only have valid statuses: 'pending', 'completed', 'cancelled'."""
        order = OrderFactory()
        for valid_status in [elem[1] for elem in Order.ORDER_STATUS_CHOICES]:
            try:
                order.status = valid_status
                order.full_clean()
                self.assertEqual(order.status, valid_status)
            except ValidationError:
                self.fail(f"ValidationError raised for valid status: {valid_status}")

    def test_order_invalid_status(self):
        """Test that setting an invalid status raises a ValidationError."""
        order = OrderFactory()
        with self.assertRaises(ValidationError):
            order.status = "invalid_status"
            order.full_clean()


    def test_order_status_update(self):
        """Test that updating the status of an Order works correctly."""
        order = OrderFactory()
        for valid_status in [elem[1] for elem in Order.ORDER_STATUS_CHOICES]:
            try:
                order.status = valid_status
                order.save()
                self.assertEqual(order.status, valid_status)
            except ValidationError:
                self.fail(f"ValidationError raised for valid status: {valid_status}")

    def test_order_user_association(self):
        """Test that an Order must be associated with a User."""
        order = OrderFactory()
        self.assertIsNotNone(order.user)

        with self.assertRaises(IntegrityError):
            OrderFactory(user=None)


    def test_order_session_association(self):
        """Test that an Order must be associated with a Session."""
        order = OrderFactory()
        self.assertIsNotNone(order.session)

        with self.assertRaises(IntegrityError):
            OrderFactory(session=None)

    def test_order_total_price_negative_validation(self):
        """Test that a negative total price raises a ValidationError."""
        order = OrderFactory()
        with self.assertRaises(ValidationError):
            order.total_price = -100
            order.full_clean()


    def test_order_created_at_auto_set(self):
        """Test that the created_at field is automatically set when an Order is created."""
        order = OrderFactory()
        self.assertIsNotNone(order.created_at)

    def test_order_updated_at_auto_update(self):
        """Test that the updated_at field is updated when an Order is modified."""
        order = OrderFactory()
        og_updated_at = order.updated_at
        time.sleep(1)
        order.status = "completed"
        order.save()
        self.assertGreater(order.updated_at, og_updated_at)


    def test_get_seat_numbers_with_tickets(self):
        """Test that the `get_seat_numbers` method returns the correct seat numbers for an Order."""
        order = OrderFactory()
        ticket = TicketFactory(order=order)
        ticket2 = TicketFactory(order=order)
        tickets = [ticket.seat_number, ticket2.seat_number]
        seat_number_list = order.get_list_seat_numbers()
        self.assertListEqual(sorted(seat_number_list), sorted(tickets))

    def test_get_seat_numbers_without_tickets(self):
        """Test that the `get_seat_numbers` method returns an empty string if no tickets are associated."""
        order = OrderFactory()
        seat_number_list = order.get_list_seat_numbers()
        self.assertListEqual(seat_number_list, [])
        seat_number_str = order.get_str_seat_numbers()
        self.assertEqual(seat_number_str, "")

    def test_order_str_method(self):
        """Test the string representation of the Order model."""
        order = OrderFactory()
        order_str = str(order)
        self.assertEqual(order_str, f"Order {order.id} for {order.user.username}")

    def test_order_deletes_related_tickets(self):
        """Test that deleting an Order deletes all related Tickets."""
        order = OrderFactory()
        order_id = order.id
        first_ticket = TicketFactory(order=order, session=order.session)
        second_ticket = TicketFactory(order=order, session=order.session)

        self.assertTrue(Ticket.objects.filter(pk=first_ticket.pk).exists())
        self.assertTrue(Ticket.objects.filter(pk=second_ticket.pk).exists())

        order.delete()

        self.assertFalse(Ticket.objects.filter(pk=first_ticket.pk).exists())
        self.assertFalse(Ticket.objects.filter(pk=second_ticket.pk).exists())

        self.assertEqual(Ticket.objects.filter(order=order_id).count(), 0)

    def test_order_deletes_related_session(self):
        """Test that deleting a Session associated with an Order raises a proper exception or handles it gracefully."""
        order = OrderFactory()
        order_id = order.id
        session = order.session
        session.delete()
        self.assertFalse(Order.objects.filter(pk=order_id).exists())


    def test_order_total_price_calculation(self):
        """Test that the total price of an Order is calculated based on associated tickets."""
        order = OrderFactory()

        expected_sum = 0
        ticket_count = random.randint(2, 6)

        for _ in range(ticket_count):
            ticket = TicketFactory(order=order, session=order.session, user=order.user)
            expected_sum += ticket.price

        order.total_price = sum(ticket.price for ticket in order.tickets.all())
        order.save()

        self.assertEqual(order.total_price, expected_sum)