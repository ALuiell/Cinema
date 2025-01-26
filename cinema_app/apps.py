from django.apps import AppConfig


class CinemaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cinema_app'

    def ready(self):
        import cinema_app.signals