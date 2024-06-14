from ditto.blockdag import Block, BlockType


class TestBlock:

    def test_init(self):
        b = Block()
        assert b.bid == 0
        assert b.type == BlockType.ORPHAN
        assert b.miner is None
        assert b.pref is None
        assert b.crefs == set()
        assert b.height == 0
        assert b.size == 0
        assert b.txs == tuple()
        assert b.data is None

    def test_hash(self):
        b = Block(1)
        assert hash(b) == 1
        b.bid = 2
        assert hash(b) == 2
