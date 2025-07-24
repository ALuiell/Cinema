from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path
from .views import MovieViewSet, SessionViewSet, OrderViewSet
from cinema_app_api.views import confirm_telegram_link

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    # Main Views
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),

    # Telegram
    path('telegram/link/confirm/', confirm_telegram_link, name='telegram_link_confirm')
]
