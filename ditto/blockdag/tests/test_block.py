from ditto.blockdag import Block, BlockType


class TestBlock:

    def test_init(self):
        b = Block()
        assert b._bid == 0
        assert type(b._type) == BlockType
        assert b._miner is None
        assert b._pref is None
        assert b._crefs == set("")
        assert b._height == 0
        assert b._size == 0
        assert b._txs == tuple()
        assert b._data is None

    def test_hash(self):
        b = Block(1)
        assert hash(b) == 1
        b._bid = 2
        assert hash(b) == 2
