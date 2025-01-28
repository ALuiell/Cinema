import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema.settings")
django.setup()

import json
from cinema_app.models import Movie, Genre

with open("movies.json", "r", encoding="utf-8") as file:
    data = json.load(file)


def set_genre(genres, movie_instance):
    genre_objects = []
    for genre_name in genres:
        genre_obj, _ = Genre.objects.get_or_create(name=genre_name)
        genre_objects.append(genre_obj)
    movie_instance.genre.set(genre_objects)

created_movies = []
skipped_movies = []

for movie in data:
    if not Movie.objects.filter(title=movie["title"]).exists():
        movie_instance = Movie.objects.create(
            title=movie["title"],
            original_name=movie["original_name"],
            description=movie["description"],
            release_date=movie["release_date"],
            duration=movie["duration"],
            age_limit=movie["age_limit"],
        )
        set_genre(movie["genre"], movie_instance)
        created_movies.append(movie["title"])
    else:
        skipped_movies.append(movie["title"])

print("Created movies:", created_movies)
print("Skipped movies (already existed):", skipped_movies)
