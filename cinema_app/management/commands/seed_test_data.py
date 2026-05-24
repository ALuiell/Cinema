import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from cinema_app.models import Genre, Movie


DEFAULT_GENRES = [
    'Action',
    'Adventure',
    'Animation',
    'Biography',
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Family',
    'Fantasy',
    'History',
    'Horror',
    'Mystery',
    'Romance',
    'Sci-Fi',
    'Thriller',
    'War',
]


class Command(BaseCommand):
    help = 'Adds default genres and up to 10 test movies to the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='How many test movies to create. Maximum: 10.',
        )

    def handle(self, *args, **options):
        requested_count = options['count']
        movie_count = max(1, min(requested_count, 10))

        with transaction.atomic():
            genres = self._create_genres()
            created_movies = self._create_movies(genres, movie_count)

        self.stdout.write(
            self.style.SUCCESS(
                f'Genres in database: {Genre.objects.count()}. Created test movies: {created_movies}.'
            )
        )

    def _create_genres(self):
        genres = []
        created_count = 0

        for genre_name in DEFAULT_GENRES:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            genres.append(genre)
            if created:
                created_count += 1

        self.stdout.write(f'Added new genres: {created_count}.')
        return genres

    def _create_movies(self, genres, movie_count):
        created_movies = 0
        next_index = 1

        while created_movies < movie_count:
            original_name = f'Movie {next_index}'
            next_index += 1

            if Movie.objects.filter(original_name=original_name).exists():
                continue

            movie = Movie.objects.create(
                title=original_name,
                original_name=original_name,
                description=f'Test description for {original_name}.',
                duration=random.randint(60, 120),
                release_date=self._random_release_date(),
                age_limit=random.choice([choice[0] for choice in Movie.AGE_CHOICES]),
                poster=None,
            )

            selected_genres = random.sample(genres, k=random.randint(1, min(3, len(genres))))
            movie.genre.set(selected_genres)
            created_movies += 1

        return created_movies

    @staticmethod
    def _random_release_date():
        start_date = date(2000, 1, 1)
        end_date = date(2026, 12, 31)
        random_days = random.randint(0, (end_date - start_date).days)
        return start_date.fromordinal(start_date.toordinal() + random_days)
