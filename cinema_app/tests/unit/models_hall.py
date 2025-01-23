from django.test import TestCase
from django.core.exceptions import ValidationError
from cinema_app.tests.factory_tests import HallFactory


class HallModelTestCase(TestCase):
    def setUp(self):
        # Create a valid Hall instance for general use in other tests
        self.valid_hall = HallFactory(name="Main Hall", capacity=100)

    def test_hall_str_method(self):
        """Test the string representation of the Hall model."""
        hall = HallFactory(name="Main Hall", capacity=100)
        self.assertEqual(str(hall), "Main Hall")

    def test_hall_capacity_zero_validation(self):
        """Test that a ValidationError is raised if the capacity is zero."""
        # Use HallFactory with build strategy to create an unsaved instance
        hall = HallFactory.build(name="Small Hall", capacity=0)
        with self.assertRaises(ValidationError):
            hall.full_clean()  # Trigger validation manually

    def test_hall_capacity_negative_validation(self):
        """Test that a ValidationError is raised if the capacity is negative."""
        hall = HallFactory.build(name="Negative Hall", capacity=-5)
        with self.assertRaises(ValidationError):
            hall.full_clean()  # Trigger validation manually

    def test_hall_capacity_valid(self):
        """Test that a Hall with valid capacity passes validation and can be saved."""
        hall = HallFactory.build(name="Valid Hall", capacity=50)
        try:
            hall.full_clean()  # Validate the model fields
            hall.save()  # Save only if validation passes
        except ValidationError:
            self.fail("Hall with valid capacity raised a ValidationError.")

    def test_hall_name_field(self):
        """Test that the name field is correctly stored."""
        self.assertEqual(self.valid_hall.name, "Main Hall")

    def test_hall_capacity_field(self):
        """Test that the capacity field is correctly stored."""
        self.assertEqual(self.valid_hall.capacity, 100)
