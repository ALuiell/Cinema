from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from cinema_app.models import Genre
from cinema_app.tests.factory_tests import GenreFactory


class GenreModelTestCase(TestCase):

    def setUp(self):
        self.genre = GenreFactory(name="Action")

    def test_genre_str_method(self):
        """Test the string representation of the Genre model."""
        genre = GenreFactory(name="Adventure")
        self.assertEqual(str(genre), "Adventure")

    def test_genre_name_unique(self):
        """Test that the name field must be unique."""
        with self.assertRaises(ValidationError):
            duplicate_genre = GenreFactory.build(name="Action")
            duplicate_genre.full_clean()

    def test_genre_name_unique_save(self):
        """Test that saving a Genre with a duplicate name raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            GenreFactory(name="Action")

    def test_genre_name_max_length(self):
        """Test the max length constraint (50 characters) for the name field."""
        genre = GenreFactory.build(name="A" * 51)
        with self.assertRaises(ValidationError):
            genre.full_clean()

    def test_genre_valid_data(self):
        """Test creating a Genre instance with valid data."""
        genre = GenreFactory.build(name="Drama")
        try:
            genre.full_clean()
            genre.save()
        except ValidationError:
            self.fail("Genre with valid data raised ValidationError.")

    def test_genre_name_field(self):
        """Test that the name field is stored correctly."""
        self.assertEqual(self.genre.name, "Action")