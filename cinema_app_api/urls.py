from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MovieViewSet, SessionViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
