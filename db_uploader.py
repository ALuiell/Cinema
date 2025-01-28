import os
import django
import random
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema.settings")
django.setup()
from cinema_app.models import Movie, Genre
from datetime import datetime, timedelta





genres = [
    "Комедія",
    "Драма",
    "Трилер",
    "Фантастика",
    "Бойовик",
    "Мелодрама",
    "Жахи",
    "Анімація",
    "Пригоди",
    "Фентезі",
    "Документальний",
    "Кримінал",
    "Мюзикл",
    "Сімейний",
    "Історичний",
    "Військовий",
    "Спортивний"
]

def set_genre(movie_instance):
    genre_objects = []
    for _ in range(2):  # Выбираем 2 случайных жанра
        genre_name = random.choice(genres)
        genre_obj, _ = Genre.objects.get_or_create(name=genre_name)
        genre_objects.append(genre_obj)
    movie_instance.genre.set(genre_objects)

for num in range(19, 100):
    movie_instance = Movie.objects.create(
        title=f"Фільм {num}",
        original_name=f"original_name {num}",
        description=f'Це опис для фільму номер {num}',
        release_date=datetime(1970, 1, 1) + timedelta(
            days=random.randint(0, (datetime(2024, 12, 31) - datetime(1970, 1, 1)).days)
        ),
        duration=random.randint(60, 280),
        age_limit=random.choice([choice[0] for choice in Movie.AGE_CHOICES]),
    )
    set_genre(movie_instance)

