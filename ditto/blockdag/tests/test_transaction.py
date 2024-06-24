from ditto.blockdag.transaction import Transaction, TransactionType


class TestTransaction:

    def test_init(self):
        t = Transaction()
        assert t.txid == 0
        assert t.ttype == TransactionType.REGULAR
        assert t.blks == set()
        assert t.note is None

    def test_hash(self):
        t = Transaction(txid=1)
        assert hash(t) == 1
        t.txid = 2
        assert hash(t) == 2
