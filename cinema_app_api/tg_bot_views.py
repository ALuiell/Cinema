from django.db import transaction, IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from cinema_app.models import *
from cinema_app.tasks import send_link_code_email
from cinema_app_api.serializers import *
from django.conf import settings


# TELEGRAM API VIEW
@api_view(['POST'])
@permission_classes([AllowAny])
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

    try:
        with transaction.atomic():
            profile.telegram_id = tg_id
            profile.use_code()  # внутри use_code() вызывается save()
    except IntegrityError:
        return Response(
            {'error': 'This Telegram account is already linked to another user.'},
            status=400
        )
    return Response({'status': 'Telegram linked successfully.'})

@api_view(['GET'])
@permission_classes([AllowAny])
def check_link_profile(request, telegram_id):
    if not TelegramProfile.objects.filter(telegram_id=telegram_id).exists():
        return Response({'error': 'Telegram profile not found.'}, status=404)
    else:
        return Response({'linked': True}, status=200)

def get_user_profile_data(user_profile):
    return {
        'first_name': user_profile.first_name or 'Not provided',
        'last_name': user_profile.last_name or 'Not provided',
        'email': user_profile.email or 'Not provided',
        'edit_link': f"{settings.WEB_APP_URL}profile/edit/{user_profile.id}/"
    }

@api_view(['GET'])
@permission_classes([AllowAny])
def user_profile_info(request, telegram_id: int):
    try:
        tg_profile = TelegramProfile.objects.get(telegram_id=telegram_id)
    except TelegramProfile.DoesNotExist:
        return Response({'error': 'Telegram profile not found.'}, status=404)

    user_profile = tg_profile.user
    profile_data = get_user_profile_data(user_profile)
    return Response(profile_data, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_orders(request, telegram_id: int):
    try:
        tg_profile = TelegramProfile.objects.get(telegram_id=telegram_id)
    except TelegramProfile.DoesNotExist:
        return Response({'error': 'Telegram profile not found.'}, status=404)

    qs = (Order.objects
          .filter(user=tg_profile.user)
          .select_related('session', 'session__hall', 'session__movie')
          .prefetch_related('tickets'))

    data = OrderBotSerializer(qs, many=True).data
    return Response({'orders': data}, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_code_email(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Missing email.'}, status=400)
    if not User.objects.filter(email=email).exists():

        return Response({'error': 'profile with this email doesnt exist, please sign in on the website.',
                         'link': f'{settings.WEB_APP_URL}accounts/register/'}, status=404)
    else:
        user = User.objects.filter(email=email).first()
        profile_data = TelegramProfile.create_instance(user, False)
        code = profile_data['code']
        send_link_code_email.delay(email, code)
        return Response({'msg': 'code send on provided email'}, status=200)
