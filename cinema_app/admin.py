from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'age_limit', 'display_genres', 'release_date')
    exclude = ('slug',)
    filter_horizontal = ('genre',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('hall', 'movie', 'session_date', 'start_time', 'end_time')
    help_texts = {
        'session_date': 'Enter the date in the format: DD/MM/YYYY',
    }
    # exclude = ('end_time',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'status',)
    readonly_fields = ('total_price', 'created_at', 'updated_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_full_name',
        'get_movie_title',
        'get_genres',
        'get_hall_name',
        'seat_number',
        'get_session_date',
        'get_session_start_time',
        'get_session_end_time',
        'price',
        'status',
    )
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('user__first_name',
                     'user__last_name',
                     'session__movie__title',
                     'session__hall__name',)
    list_filter = (
        'session__hall',
        'session__session_date',
        'session__movie',
        'session__start_time',
        'session__end_time',
    )

    def get_user_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    get_user_full_name.short_description = 'Користувач'

    def get_movie_title(self, obj):
        return obj.session.movie.title
    get_movie_title.short_description = 'Фільм'

    def get_genres(self, obj):
        return obj.session.movie.display_genres()
    get_genres.short_description = 'Жанри'

    def get_session_date(self, obj):
        return obj.session.session_date
    get_session_date.short_description = 'Дата сеансу'

    def get_session_start_time(self, obj):
        return obj.session.start_time
    get_session_start_time.short_description = "Початок сеансу"

    def get_session_end_time(self, obj):
        return obj.session.end_time
    get_session_end_time.short_description = "Кінець сеансу"

    def get_hall_name(self, obj):
        return obj.session.hall.name
    get_hall_name.short_description = 'Зал'
