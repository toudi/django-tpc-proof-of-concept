from django.core.management.base import BaseCommand
from tpc.atomic_tpc import commit_prepared


class Command(BaseCommand):
    def handle(self, *args, **options):
        txn_id = 'tpc-foo'
        commit_prepared(txn_id)
