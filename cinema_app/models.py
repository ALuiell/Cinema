from datetime import time, timedelta, datetime, date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from .utils import poster_upload_to, generate_session_slug
import re


class Hall(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Зал")
    capacity = models.PositiveIntegerField(verbose_name='Кількість місць')

    def clean(self, *args, **kwargs):
        if self.capacity is None or self.capacity <= 0:
            raise ValidationError("The capacity must be greater than zero.")

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Жанр')

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
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['release_date']),
        ]

    def get_absolute_url(self):
        # Генерирует URL для страницы деталей фильма
        return reverse('movie_detail', args=[self.slug])

    def display_genres(self):
        return ', '.join([genre.name for genre in self.genre.all()])

    display_genres.short_description = 'Жанри'

    def clean(self):
        pattern = r"^[A-Za-z0-9\s:,'\-&!?.]+$"
        if not re.match(pattern, self.original_name):
            raise ValidationError("Original name must contain only English characters, numbers, and valid punctuation.")

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
    slug = models.SlugField(max_length=255, unique=True, editable=False, blank=True)

    class Meta:
        unique_together = ('hall', 'session_date', 'start_time')
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

    def save(self, *args, **kwargs):
        if self.start_time and self.movie:
            duration = timedelta(minutes=self.movie.duration + 15)
            datetime_start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
            datetime_end = datetime_start + duration
            self.end_time = (datetime.min + datetime_end).time()
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

    def get_seat_numbers(self):
        return ', '.join(str(ticket.seat_number) for ticket in self.tickets.all())

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    def clean(self):
        if not self.user:
            raise ValidationError("User must be specified for the order.")

        if not self.session:
            raise ValidationError("Session must be specified for the order.")

        if self.status not in dict(self.ORDER_STATUS_CHOICES):
            raise ValidationError("Invalid status for the order.")

        if self.total_price < 0:
            raise ValidationError("Total price cannot be negative.")


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

    def clean(self):
        hall_capacity = self.session.hall.capacity
        if self.seat_number is None or hall_capacity is None or not (1 <= self.seat_number <= hall_capacity):
            raise ValidationError(
                f"Номер місця має бути від 1 до {hall_capacity}."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (f'{self.user.first_name} {self.user.last_name} | '
                f' {self.session.movie} | {self.session}')
