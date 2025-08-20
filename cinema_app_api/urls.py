from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path
from .views import MovieViewSet, SessionViewSet, OrderViewSet
from cinema_app_api.tg_bot_views import confirm_telegram_link, check_link_profile, user_profile_info, user_orders, send_code_email

router = DefaultRouter()
'''
GET    /api/movies/           # list           | name='movie-list'
POST   /api/movies/           # create         | name='movie-list'

GET    /api/movies/{id}/      # retrieve       | name='movie-detail'
PUT    /api/movies/{id}/      # update         | name='movie-detail'
PATCH  /api/movies/{id}/      # partial_update | name='movie-detail'
DELETE /api/movies/{id}/      # destroy        | name='movie-detail'
'''
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
    path('telegram/link/check/<int:telegram_id>/',  check_link_profile, name='telegram_link_check'),
    path('telegram/user/info/<int:telegram_id>/',  user_profile_info, name='get_user_info'),
    path('telegram/user/orders/<int:telegram_id>/', user_orders, name='tg_user_orders'),
    path('telegram/send-email/', send_code_email, name='send_email'),
]
