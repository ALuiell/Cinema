from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from cinema_app_api.permissions import IsManager
from rest_framework.viewsets import ModelViewSet
from cinema_app_api.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.exceptions import ValidationError, PermissionDenied
from cinema_app.models import *

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


@api_view(['POST'])
def confirm_telegram_link(request):
    raw_code = request.data.get('code')
    tg_id = request.data.get('tg_id')
    if not raw_code or not tg_id:
        return Response({'error': 'Missing code or tg_id.'}, status=400)

    try:
        tg_id = int(tg_id)
    except (ValueError, TypeError):
        return Response( {'error': '"tg_id" must be an integer.'}, status=400)

    hashed = TelegramProfile.convert_in_hash(raw_code)
    try:
        profile = TelegramProfile.objects.get(verification_code_hash=hashed)
    except TelegramProfile.DoesNotExist:
        return Response({'error': 'Invalid code.'}, status=400)

    if not profile.is_valid():
        return Response({'error': 'Code expired or already used.'}, status=400)

    profile.telegram_id = int(tg_id)
    profile.use_code()
    return Response({'status': 'Telegram linked successfully.'})



# class UserProfileViewSet(viewsets.ViewSet):
#     permission_classes = [AllowAny]
#
#     def create(self, request):
#         tg_id = request.data.get("telegram_id")
#
#         if not tg_id:
#             return Response({"detail": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             tg_id = int(tg_id)
#         except ValueError:
#             return Response({"detail": "Invalid telegram_id"}, status=status.HTTP_400_BAD_REQUEST)
#
#         user = get_object_or_404(User, telegram_id=tg_id)
#         if user.telegram_id != tg_id:
#             return Response({"detail": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
#         data = UserProfileSerializer(user).data
#
#         '''action for response to user edit_link'''
#         # @action(detail=False, methods=["post"])
#         # def edit(self, request):
#             # data["edit_link"] = f"https://your-site.com/profile/edit/{user.id}/"
#
#         return Response(data)