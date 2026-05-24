from django.core.management.base import BaseCommand

from cinema_app.tasks import cancel_unpaid_orders_logic


class Command(BaseCommand):
    help = 'Cancels pending orders that have not been paid within the expiration window.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=15,
            help='Age threshold in minutes for pending orders. Default: 15.',
        )

    def handle(self, *args, **options):
        expiration_minutes = options['minutes']
        canceled_count = cancel_unpaid_orders_logic(expiration_minutes=expiration_minutes)
        self.stdout.write(
            self.style.SUCCESS(
                f'Cancelled unpaid orders: {canceled_count} (threshold: {expiration_minutes} minutes).'
            )
        )
