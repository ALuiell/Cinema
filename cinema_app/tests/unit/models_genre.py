from django.test import TestCase
from django.core.exceptions import ValidationError
from cinema_app.models import Genre


class GenreModelTestCase(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(name="Action")

    def test_genre_str_method(self):
        """Test the string representation of the Genre model."""
        genre = Genre(name="Adventure")
        self.assertEqual(str(genre), "Adventure")

    def test_genre_name_unique(self):
        """Test that the name field must be unique."""
        with self.assertRaises(ValidationError):
            duplicate_genre = Genre(name="Action")
            duplicate_genre.full_clean()  # Validate the uniqueness constraint

    def test_genre_name_max_length(self):
        """Test the max length constraint (50 characters) for the name field."""
        genre = Genre(name="A" * 51)  # Length of 51 characters
        with self.assertRaises(ValidationError):
            genre.full_clean()  # This will raise a ValidationError due to max_length

    def test_genre_valid_data(self):
        """Test creating a Genre instance with valid data."""
        genre = Genre(name="Drama")
        try:
            genre.full_clean()  # Validate the model fields
            genre.save()
        except ValidationError:
            self.fail("Genre with valid data raised ValidationError.")

    def test_genre_name_field(self):
        """Test that the name field is stored correctly."""
        self.assertEqual(self.genre.name, "Action")