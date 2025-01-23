from datetime import time, date, timedelta, datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from cinema_app.models import Session, Genre
from cinema_app.tests.factory_tests import SessionFactory
from django.db.utils import IntegrityError


class SessionModelTestCase(TestCase):
    def setUp(self):
        """Set up reusable objects for testing."""
        self.session = SessionFactory()

    def test_session_creation(self):
        """Test successful creation of a Session."""
        self.assertEqual(self.session.base_ticket_price, 100.00)
        self.assertIsNotNone(self.session.hall)
        self.assertIsNotNone(self.session.movie)

    def test_session_genre_relationship(self):
        """Test that the session's movie has related genres."""
        self.assertGreater(self.session.movie.genre.count(), 0)
        genre = self.session.movie.genre.first()
        self.assertIsInstance(genre, Genre)

    def test_end_time_calculation(self):
        """Test that the end_time is correctly calculated."""
        session = SessionFactory(
            session_date = date.today() + timedelta(days=1),
            start_time=time(15, 0)  # 3:00 PM
        )
        expected_end_time = (datetime.min + timedelta(
            hours=15, minutes=0
        ) + timedelta(
            minutes=(self.session.movie.duration + 15)  # Movie duration + 15 min
        )).time()
        self.assertEqual(session.end_time, expected_end_time)

    def test_positive_ticket_price_validation(self):
        """Test validation for positive base_ticket_price."""
        session = SessionFactory.build(
            base_ticket_price=-10.00,  # Invalid
            session_date = date.today() + timedelta(days=1),
            start_time=time(13, 0)
        )
        with self.assertRaises(ValidationError):
            session.clean()

    def test_session_date_not_in_past(self):
        """Ensure the session date cannot be set in the past."""
        session = SessionFactory.build(
            session_date=date(2020, 1, 1),  # Past date
            start_time=time(16, 0)
        )
        with self.assertRaises(ValidationError):
            session.clean()

    def test_session_start_time_valid_range(self):
        """Ensure session start_time falls within valid range (10:00 to 23:59)."""
        # Start time before 10:00
        session = SessionFactory.build(
            session_date = date.today() + timedelta(days=1),
            start_time=time(9, 0)  # Invalid
        )
        with self.assertRaises(ValidationError):
            session.clean()

        # Start time after 23:59
        session.start_time = time(0, 0)  # Invalid
        with self.assertRaises(ValidationError):
            session.clean()

        # Valid time
        session.start_time = time(10, 30)  # Valid
        try:
            session.clean()
        except ValidationError:
            self.fail("ValidationError raised for a valid time range.")

    def test_session_start_time_today_not_in_past(self):
        """Test that the session start_time today must not be in the past."""
        session = Session(
            session_date=date.today(),
            start_time=(datetime.now() - timedelta(hours=1)).time()  # One hour in the past
        )
        with self.assertRaises(ValidationError):
            session.clean()

    def test_unique_constraint(self):
        """Test unique constraint for hall, session_date, and start_time."""
        # added validator to models
        session = SessionFactory(
            session_date = date.today() + timedelta(days=1),
            start_time=time(14, 0)
        )
        with self.assertRaises(ValidationError):  # Restricted by unique constraint
            SessionFactory(
                hall=session.hall,
                session_date=date.today(),
                start_time=time(14, 0)  # Duplicate session in same hall at same time
            )

    def test_absolute_url(self):
        """Test the get_absolute_url method."""
        session = SessionFactory()
        url = session.get_absolute_url()
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith("/"))

    def test_string_representation(self):
        """Test the `__str__` method of the Session model."""
        session = SessionFactory()
        self.assertEqual(str(session), f"{session.hall} | {session.session_date} | {session.start_time}")