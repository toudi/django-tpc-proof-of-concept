from django.core.management.base import BaseCommand
from tpc.models import MyModel
from tpc.atomic_tpc import atomic
from django.db import transaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        with atomic(transaction_id='tpc-foo'):
            MyModel.objects.create(foo='123')
            sid = transaction.savepoint()
            try:
                with atomic(transaction_id='tpc-foo'):
                    MyModel.objects.create(foo='1234')
                    raise ValueError('intentional exception')
            except ValueError:
                transaction.savepoint_rollback(sid)
