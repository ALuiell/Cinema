from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from social_core.pipeline import user

from cinema_app_api.permissions import IsManager
from rest_framework.viewsets import ModelViewSet
from cinema_app_api.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.exceptions import ValidationError, PermissionDenied

# Create your views here.


# add filtered
class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['genre', 'age_limit']
    search_fields = ['original_name', 'description', 'title']

    default_permissions = [IsAuthenticatedOrReadOnly]
    manager_permissions = [IsManager]


    def get_permissions(self):
        if self.action in ('create', 'partial_update', 'destroy'):
            return [perm() for perm in self.manager_permissions]
        return [perm() for perm in self.default_permissions]

# add optimization for database requests
# add payment link in response
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['session_date', 'start_time']

    default_permissions = [IsAuthenticatedOrReadOnly]
    manager_permissions = [IsManager]

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        session = self.get_object()
        seats = session.get_available_seats()
        return Response({'seats': seats})

    def get_permissions(self):
        if self.action in ('create', 'partial_update', 'destroy'):
            return [perm() for perm in self.manager_permissions]
        return [perm() for perm in self.default_permissions]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    default_permissions = [IsAuthenticated]
    manager_permissions = [IsManager]
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderDetailSerializer

    def get_permissions(self):
        if self.action in ('partial_update', 'destroy', 'update'):
            return [perm() for perm in self.manager_permissions]
        return [perm() for perm in self.default_permissions]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if not (request.user == order.user or request.user.groups.filter(name='Manager').exists()):
            raise PermissionDenied("You do not have permission to cancel this order.")

        if order.status == Order.CANCELLED:
            raise ValidationError("Order has already been cancelled.")
        if order.status == Order.COMPLETED:
            raise ValidationError("Cannot cancel a completed order.")

        order.status = Order.CANCELLED
        order.save()
        return Response({'status': order.status})

def profile(request):
    pass