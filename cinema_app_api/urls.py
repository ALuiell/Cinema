from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path
from .views import MovieViewSet, SessionViewSet, OrderViewSet
from cinema_app_api.views import confirm_telegram_link, check_link_profile

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
    path('telegram/link/confirm/', confirm_telegram_link, name='telegram_link_confirm'),
    path('telegram/link/check/<int:telegram_id>',  check_link_profile, name='telegram_link_check')
]
