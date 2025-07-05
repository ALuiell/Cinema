from datetime import time, timedelta, datetime, date
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from .utils import poster_upload_to, generate_session_slug
import re


class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_id = models.BigIntegerField(unique=True,
                                         null=True,
                                         blank=True,
                                         help_text="Telegram user ID"
                                         )
    verification_code = models.CharField(unique=True,
                                         null=True,
                                         blank=True,
                                         max_length=6,
                                         help_text="Verification telegram code")


    def __str__(self):
        return self.user.username


class Hall(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Зал")
    capacity = models.PositiveIntegerField(verbose_name='Кількість місць')

    def clean(self, *args, **kwargs):
        if self.capacity is None or self.capacity == 0:
            raise ValidationError({'capacity': "The capacity must be greater than zero."})

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Жанр')

    @staticmethod
    def genre_list():
        return [genre.name for genre in Genre.objects.all()]

    def __str__(self):
        return self.name


class Movie(models.Model):
    AGE_CHOICES = [
        (0, 'Для всіх'),
        (6, '6+'),
        (12, '12+'),
        (16, '16+'),
        (18, '18+'),
    ]

    title = models.CharField(max_length=100, verbose_name='Назва')
    original_name = models.CharField(max_length=100, verbose_name='Оригінальна назва')
    description = models.TextField(verbose_name='Опис')
    duration = models.PositiveIntegerField(verbose_name='Тривалість (хвилини)')
    genre = models.ManyToManyField(Genre, related_name='movies', verbose_name='Жанри')
    release_date = models.DateField(verbose_name='Дата випуску')
    age_limit = models.PositiveIntegerField(choices=AGE_CHOICES, verbose_name='Вікове обмеження')
    poster = models.ImageField(upload_to=poster_upload_to, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['release_date']),
        ]

    def get_absolute_url(self):
        return reverse('movie_detail', args=[self.slug])

    def display_genres(self):
        return ', '.join([genre.name for genre in self.genre.all()])

    display_genres.short_description = 'Жанри'

    def clean(self):
        super().clean()
        pattern = r"^[A-Za-z0-9\s:,'\-&!?.]+$"
        if not re.match(pattern, self.original_name):
            raise ValidationError({'original_name': "Original name must contain only English characters."})

        valid_age_limits = [choice[0] for choice in self.AGE_CHOICES]
        if self.age_limit not in valid_age_limits:
            raise ValidationError(f"Age limit {self.age_limit} is not valid.")

        if self.duration is None or self.duration <= 0:
            raise ValidationError("The duration must be greater than zero.")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.original_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Session(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name='Зал')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='Фільм')
    base_ticket_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    session_date = models.DateField(verbose_name='Дата сеансу')
    start_time = models.TimeField(verbose_name='Початок сеансу')
    end_time = models.TimeField(verbose_name='Кінець сеансу', blank=True, null=True, editable=False)
    slug = models.SlugField(max_length=255, unique=True, editable=False, blank=True, default='')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['hall', 'session_date', 'start_time'], name='unique_session_time')
        ]
        indexes = [
            models.Index(fields=['session_date', 'start_time']),
            models.Index(fields=['hall']),
            models.Index(fields=['movie']),
        ]

    def get_available_seats(self):
        booked_tickets = (Ticket.objects.filter(session=self)
                          .exclude(status='cancelled')
                          .values_list('seat_number',
                                       flat=True))
        total_seats = self.hall.capacity
        available_seats = [seat for seat in range(1, total_seats + 1) if seat not in booked_tickets]
        return available_seats


    def get_seats_by_row(self):
        seats_per_row = 10
        row_capacity = self.hall.capacity // seats_per_row
        available_seats = self.get_available_seats()

        rows = []
        for row in range(row_capacity):
            current_row = []
            for seat_number in range(1, seats_per_row + 1):
                seat_id = row * seats_per_row + seat_number
                status = 'Free' if seat_id in available_seats else 'Booked'
                current_row.append((seat_id, status))
            rows.append(current_row)

        return rows

    def get_absolute_url(self):
        return reverse('session_detail', kwargs={'slug': self.slug})

    def clean(self):
        # Ensure the base ticket price is a positive number
        if self.base_ticket_price is None or self.base_ticket_price <= 0:
            raise ValidationError("The ticket price must be greater than zero.")

        # Validate that the session date is today or in the future
        if self.session_date is None:
            raise ValidationError("The session date cannot be empty.")
        elif self.session_date < date.today():
            raise ValidationError("The session date cannot be in the past.")

        # Check if start time is provided and within the allowed range
        if self.start_time is None:
            raise ValidationError("Start time must be a valid time.")
        elif not (time(10, 0) <= self.start_time <= time(23, 59)):
            raise ValidationError("The session must start between 10:00 AM and 12:00 AM.")

        # Ensure the session date and start time are logically consistent
        if self.session_date == date.today() and self.start_time < datetime.now().time():
            raise ValidationError("The session start time cannot be in the past.")

    def calculate_end_time(self):
        if self.start_time and self.movie:
            duration = timedelta(minutes=self.movie.duration + 15)
            datetime_start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
            datetime_end = datetime_start + duration
            return (datetime.min + datetime_end).time()
        return None

    def save(self, *args, **kwargs):
        self.end_time = self.calculate_end_time()
        self.slug = generate_session_slug(self)
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.hall} | {self.session_date} | {self.start_time}'


class Order(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    ORDER_STATUS_CHOICES = [
        (PENDING, 'pending'),
        (COMPLETED, 'completed'),
        (CANCELLED, 'cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_str_seat_numbers(self):
        return ', '.join(str(ticket.seat_number) for ticket in self.tickets.all())

    def get_list_seat_numbers(self):
        return [ticket.seat_number for ticket in self.tickets.all()]

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    def clean(self):

        if self.user_id is None:
            raise ValidationError("Користувач є обов'язковим для створення замовлення.")

        if self.session_id is None:
            raise ValidationError("Сеанс повинен бути вказаний для замовлення.")

        if self.status not in dict(self.ORDER_STATUS_CHOICES):
            raise ValidationError("Недійсний статус для замовлення.")

        if self.total_price < 0:
            raise ValidationError("Загальна ціна не може бути від'ємною.")


class Ticket(models.Model):
    CANCELLED = 'cancelled'
    RESERVED = 'reserved'
    BOOKED = 'booked'

    ORDER_STATUS_CHOICES = [
        (RESERVED, 'reserved'),
        (BOOKED, 'booked'),
        (CANCELLED, 'cancelled'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна", editable=False)
    seat_number = models.PositiveIntegerField(verbose_name='Номер місця', db_index=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=RESERVED)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['session', 'seat_number']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['session', 'seat_number'], name='unique_seat_per_session')
        ]

    def clean(self):
        if self.order_id is None:
            raise ValidationError("Номер замовлення обов'язковий для створення квитка.")

        if self.user_id is None:
            raise ValidationError("Користувач обов'язковий для створення квитка.")

        if self.user_id != self.order.user.id:
            raise ValidationError("Користувач квитка не відповідає користувачу замовлення.")

        if self.price == None or self.price <= 0:
            raise ValidationError('Некоректна ціна квитка')

        if self.status not in [elem[0] for elem in self.ORDER_STATUS_CHOICES]:
            raise ValidationError('Некоректний статус квитка')

        if self.seat_number not in self.session.get_available_seats():
            raise ValidationError(f'Квиток з таким номером місця вже існує')

        hall_capacity = self.session.hall.capacity
        if self.seat_number is None or hall_capacity is None or not (1 <= self.seat_number <= hall_capacity):
            raise ValidationError(
                f"Номер місця має бути від 1 до {hall_capacity}."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} | {self.session.movie} | {self.session}'
