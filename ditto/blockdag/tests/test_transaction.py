from ditto.blockdag.transaction import Transaction, TransactionType


class TestTransaction:

    def test_init(self):
        t = Transaction()
        assert t.tid == 0
        assert t.type == TransactionType.REGULAR
        assert t.blks == set()
        assert t.note is None

    def test_hash(self):
        t = Transaction(tid=1)
        assert hash(t) == 1
        t.tid = 2
        assert hash(t) == 2
