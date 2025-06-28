from datetime import datetime
from django.contrib.auth.models import User
from cinema_app.models import Movie, Order, Ticket, Session, Hall, Genre
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        exclude = ('slug',)


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        exclude = ('slug', 'end_time')


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'seat_number', 'price', 'status']


class OrderCreateSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(
        queryset=Session.objects.all()
    )
    seats = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        help_text="list seats number for reservations"
    )
    tickets = TicketSerializer(source='tickets', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'session', 'seats', 'status', 'total_price', 'tickets']
        read_only_fields = ['id', 'status', 'total_price', 'tickets']

    def validate_session(self, session):
        session_dt = timezone.make_aware(
            datetime.combine(session.session_date, session.start_time),
            timezone.get_current_timezone()
        )
        if session_dt <= timezone.now():
            raise serializers.ValidationError("The session has already started or completed.")
        return session

    def validate(self, attrs):
        # availability check
        session = attrs.get('session')
        seats = attrs.get('seats', [])
        available = session.get_available_seats()
        unavailable = [seat for seat in seats if seat not in available]
        if unavailable:
            raise serializers.ValidationError(
                f"Seats {unavailable} not available for the selected location"
            )
        return attrs

    def create(self, validated_data):
        seats = validated_data.pop('seats')
        user = self.context['request'].user
        session = validated_data['session']

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                session=session
            )
            total = 0
            for seat in seats:
                ticket = Ticket.objects.create(
                    order=order,
                    session=session,
                    seat_number=seat,
                    price=session.base_ticket_price,
                    user=user
                )
                total += ticket.price

            order.total_price = total
            order.save()

        return order

class OrderDetailSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(source='tickets', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'session',
            'status', 'total_price',
            'created_at', 'updated_at',
            'tickets'
        ]
        read_only_fields = fields

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', "last_name",  'email',)
