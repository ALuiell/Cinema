from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from cinema_app.tests.factory_tests import MovieFactory, GenreFactory
from cinema_app.models import Movie

#REWORK
class MovieModelTestCase(TestCase):
    def setUp(self):
        """Sets up initial test data for the Movie model."""
        self.genre1 = GenreFactory(name="Action")
        self.genre2 = GenreFactory(name="Drama")

        # Create a movie object
        self.movie = MovieFactory(
            title="Test Movie",
            original_name="Test Original",
            description="This is a test description.",
            genre=[self.genre1, self.genre2])

    def test_movie_creation(self):
        """Test that a Movie object is created successfully."""
        self.assertIsNotNone(self.movie.pk, "Movie object should have a primary key after being saved.")
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(self.movie.original_name, "Test Original")
        self.assertEqual(self.movie.description, "This is a test description.")
        self.assertEqual(self.movie.duration, 120)
        self.assertEqual(self.movie.age_limit, 16)

    def test_movie_genre_relationship(self):
        """Test the ManyToMany relationship between Movie and Genre."""
        genres = self.movie.genre.all()
        self.assertEqual(genres.count(), 2)
        self.assertIn(self.genre1, genres)
        self.assertIn(self.genre2, genres)

    def test_movie_str_method(self):
        """Test the __str__ method of the Movie model."""
        self.assertEqual(str(self.movie), self.movie.title)

    def test_movie_slug_creation(self):
        """Ensure the movie creates a slug based on the original_name."""
        self.assertEqual(self.movie.slug, "test-original")

        # Update the original_name and save again to test slug updates
        self.movie.original_name = "Updated Movie Name"
        self.movie.save()
        self.assertEqual(self.movie.slug, "updated-movie-name")

    def test_movie_display_genres(self):
        """Test the display_genres method of the Movie model."""
        self.assertEqual(self.movie.display_genres(), "Action, Drama")

    def test_movie_clean_valid_original_name(self):
        """Test the clean method validates original_name with the correct format."""
        self.movie.original_name = "A Valid Name 123!?"
        try:
            self.movie.clean()
        except ValidationError:
            self.fail("ValidationError raised for a valid original_name.")

    def test_movie_clean_invalid_original_name(self):
        """Test the clean method raises ValidationError for invalid original_name."""
        self.movie.original_name = "Інвалід Нейм"  # Invalid characters (non-English)
        with self.assertRaises(ValidationError):
            self.movie.clean()

    def test_clean_negative_duration(self):
        #can be IntegrationError
        movie = MovieFactory.build(
            title="Invalid Movie",
            original_name="Invalid Original Name",
            description="Test Description",
            duration=-1,
        )
        with self.assertRaises(ValidationError):
            movie.full_clean()

    def test_db_constraint_negative_duration(self):
        with self.assertRaises(IntegrityError):
            MovieFactory(
                title="Invalid Movie",
                original_name="Invalid Original Name",
                description="Test Description",
                duration=-1,
            )

    def test_movie_release_date_in_future(self):
        """Test that a movie can have a release_date in the future."""
        future_movie = MovieFactory(
            title="Future Movie",
            original_name="Future Original",
            description="Test Future Description",
            release_date=date(2025, 1, 1),  # Future date

        )
        self.assertEqual(future_movie.release_date, date(2025, 1, 1))

    def test_movie_age_limit_choices(self):
        """Test that only valid age_limit choices can be used."""
        valid_movie = MovieFactory(
            title="Child Movie",
            original_name="Child Movie Original",
            description="Test Child Description",
            release_date=date(2022, 12, 1),
            age_limit=12,  # Valid age limit
        )
        self.assertEqual(valid_movie.age_limit, 12)

        # Test invalid age limit
        with self.assertRaises(ValidationError):
            invalid_movie = MovieFactory.build(
                title="Invalid Age Movie",
                original_name="Invalid Age Movie Original",
                description="Test Invalid Age Description",
                release_date=date(2022, 12, 1),
                age_limit=99,  # Invalid age limit
            )
            invalid_movie.clean()


    def test_movie_absolute_url(self):
        """Test the get_absolute_url method."""
        url = self.movie.get_absolute_url()
        self.assertTrue(url.startswith("/"), "get_absolute_url should return a valid URL relative path.")

    def test_movie_indexing(self):
        """Test that the movie's database indexes work correctly."""
        # Ensure Movie is indexed by release_date
        indexed_field = Movie._meta.indexes[0].fields
        self.assertIn("release_date", indexed_field, "release_date should be indexed.")