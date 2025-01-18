from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from cinema_app.models import Ticket, Session, Order


#REWORK
class TicketModelTestCase(TestCase):

    def setUp(self):
        """Sets up initial test data for the Ticket model."""
        self.session1 = Session.objects.create(
            title="Test Session 1",
            description="This is a test session description.",
            release_date=date(2025, 1, 1),
            duration=120,
        )

        self.ticket = Ticket.objects.create(
            session=self.session1,
            price=10.00,
            quantity=1,
        )
