from django.test import TestCase
from django.core.exceptions import ValidationError
from cinema_app.models import Hall
from cinema_app.factory_tests import HallFactory



class HallModelTestCase(TestCase):

    def setUp(self):
        self.valid_hall = HallFactory()
        self.valid_hall.save()

    def test_hall_str_method(self):
        """Test the string representation of the Hall model."""
        hall = Hall(name="Main Hall", capacity=100)
        self.assertEqual(str(hall), "Main Hall")

    def test_hall_capacity_positive_validation(self):
        """Test that a ValidationError is raised if the capacity is zero or negative."""
        hall = Hall(name="Small Hall", capacity=0)
        with self.assertRaises(ValidationError):
            hall.clean()

    def test_hall_capacity_negative_validation(self):
        """Test negative value for capacity."""
        hall = Hall(name="Test Hall", capacity=-10)
        with self.assertRaises(ValidationError):
            hall.clean()

    def test_hall_capacity_valid(self):
        """Test that a hall with valid capacity can be saved."""
        hall = Hall(name="Valid Hall", capacity=50)
        try:
            hall.full_clean()  # Validate the model fields
            hall.save()
        except ValidationError:
            self.fail("Hall with valid capacity raised ValidationError.")

    def test_hall_name_field(self):
        """Test that the name field is stored correctly."""
        self.assertEqual(self.valid_hall.name, "Main Hall")

    def test_capacity_field(self):
        """Test that the capacity field is stored correctly."""
        self.assertEqual(self.valid_hall.capacity, 100)