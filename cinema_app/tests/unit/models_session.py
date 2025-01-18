from datetime import time, date, timedelta, datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from cinema_app.models import Hall, Movie, Session, Genre


class SessionModelTests(TestCase):
    def setUp(self):
        """Set up reusable objects for testing."""
        self.hall = Hall.objects.create(
            name="Test Hall",
            capacity=100
        )
        self.genre = Genre.objects.create(name="Action")
        self.movie = Movie.objects.create(
            title="Test Movie",
            original_name="Original Name",
            description="A test movie description.",
            duration=120,  # in minutes
            release_date=date(2023, 1, 1),
            age_limit=16
        )
        self.movie.genre.add(self.genre)

    def test_session_creation(self):
        """Test successful creation of a Session."""
        session = Session.objects.create(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=30.00,
            session_date=date.today(),
            start_time=time(14, 0)  # 2:00 PM
        )
        self.assertEqual(session.hall, self.hall)
        self.assertEqual(session.movie, self.movie)
        self.assertEqual(session.base_ticket_price, 30.00)
        self.assertEqual(session.session_date, date.today())
        self.assertEqual(session.start_time, time(14, 0))

    def test_end_time_calculation(self):
        """Test that the end_time is correctly calculated."""
        session = Session.objects.create(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=40.00,
            session_date=date.today(),
            start_time=time(15, 0)  # 3:00 PM
        )
        expected_end_time = (datetime.min + timedelta(
            hours=15, minutes=0
        ) + timedelta(
            minutes=(self.movie.duration + 15)  # Movie duration + 15 min
        )).time()
        self.assertEqual(session.end_time, expected_end_time)

    def test_positive_ticket_price_validation(self):
        """Test validation for positive base_ticket_price."""
        session = Session(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=-10.00,  # Invalid
            session_date=date.today(),
            start_time=time(13, 0)
        )
        with self.assertRaises(ValidationError):
            session.clean()

    def test_session_date_not_in_past(self):
        """Ensure the session date cannot be set in the past."""
        session = Session(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=20.00,
            session_date=date(2020, 1, 1),  # Past date
            start_time=time(16, 0)
        )
        with self.assertRaises(ValidationError):
            session.clean()

    def test_session_start_time_valid_range(self):
        """Ensure session start_time falls within valid range (10:00 to 23:59)."""
        # Start time before 10:00
        session = Session(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=20.00,
            session_date=date.today(),
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
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=15.00,
            session_date=date.today(),
            start_time=(datetime.now() - timedelta(hours=1)).time()  # One hour in the past
        )
        with self.assertRaises(ValidationError):
            session.clean()

    def test_unique_constraint(self):
        """Test unique constraint for hall, session_date, and start_time."""
        Session.objects.create(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=50.00,
            session_date=date.today(),
            start_time=time(14, 0)
        )
        with self.assertRaises(Exception):  # Restricted by unique constraint
            Session.objects.create(
                hall=self.hall,
                movie=self.movie,
                base_ticket_price=40.00,
                session_date=date.today(),
                start_time=time(14, 0)  # Duplicate session in same hall at same time
            )

    def test_absolute_url(self):
        """Test the get_absolute_url method."""
        session = Session.objects.create(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=25.00,
            session_date=date.today(),
            start_time=time(12, 0)
        )
        url = session.get_absolute_url()
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith("/"))

    def test_string_representation(self):
        """Test the `__str__` method of the Session model."""
        session = Session.objects.create(
            hall=self.hall,
            movie=self.movie,
            base_ticket_price=50.00,
            session_date=date.today(),
            start_time=time(10, 0)
        )
        self.assertEqual(str(session), f"{self.hall} | {session.session_date} | {session.start_time}")