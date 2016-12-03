from django.db.transaction import Atomic, get_connection
from django.db import DEFAULT_DB_ALIAS


class AtomicTPC(Atomic):
    def __init__(self, transaction_id, using=None, savepoint=None):
        self.transaction_id = transaction_id
        super(AtomicTPC, self).__init__(using, savepoint)

    def _commit(self):
        connection = get_connection(self.using)
        connection.connection.tpc_prepare()
        connection.commit = connection.commit_original
        delattr(connection, 'commit_original')
        connection.in_atomic_block = True

    def __enter__(self):
        connection = get_connection(self.using)
        if not hasattr(connection, 'tpc_prepared'):
            connection.tpc_prepared = True
            connection.ensure_connection()
            connection.set_autocommit(False)
            txn_id = connection.connection.xid(0, self.transaction_id, '')
            connection.connection.tpc_begin(txn_id)
            connection.in_atomic_block = False
            connection.commit_original = connection.commit
            connection.commit = self._commit
        else:
            super(AtomicTPC, self).__enter__()


def atomic(transaction_id, using=None, savepoint=True):
    # Bare decorator: @atomic -- although the first argument is called
    # `using`, it's actually the function being decorated.
    if callable(using):
        return AtomicTPC(transaction_id, DEFAULT_DB_ALIAS, savepoint)(using)
    # Decorator: @atomic(...) or context manager: with atomic(...): ...
    else:
        return AtomicTPC(transaction_id, using, savepoint)


def commit_prepared(transaction_id, using=None):
    connection = get_connection(using)
    connection.set_autocommit(False)
    txn_id = connection.connection.xid(0, transaction_id, '')
    connection.connection.tpc_commit(txn_id)
    connection.set_autocommit(True)
