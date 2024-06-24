from ditto.blockdag import BlockDAG, BlockType, Block
from ditto.network import Network
from ditto.nodes import Miner, SimpleRef


class TestMiner:

    def test_init(self):
        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        assert m._name == 'testMiner'
        assert len(m._blockdag) == 0
        assert m._max_peer_num == 10
        assert m._genesis_block == 0
        assert m._network is None
        assert len(m._mined_blocks) == 0
        assert len(m._block_queue) == 0
        assert m._refer_handler is None

    def test_mine_block(self):
        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        assert m.mine_block() is None

        net = Network()
        m.set_network(net)
        assert m.mine_block() is None

        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
        m.set_genesis_block(b1)
        assert len(m._blockdag) == 1
        assert m.get_genesis_block() == 1
        assert m.mine_block() is None

        m.set_refer_handler(SimpleRef)

        b2 = m.mine_block()
        m.add_block(b2)
        assert len(m._blockdag) == 2
        assert hash(b2) in m

        b3 = m.mine_block()
        m.add_block(b3)
        assert len(m._blockdag) == 3
        assert hash(b3) in m

    def test_queue_block(self):
        net = Network()
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)

        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        m.set_network(net)
        m.set_genesis_block(b1)
        m.set_refer_handler(SimpleRef)

        b2 = m.mine_block()
        b3 = m.mine_block()
        m._blockdag.cut_block(hash(b2))

        m.add_block(b3)
        assert m._block_queue.nodes.keys() == {hash(b2), hash(b3)}
        assert m._block_queue.edges.keys() == {(hash(b3), hash(b2))}
        assert m._block_queue.nodes[hash(b2)][Miner._QUEUE_BLOCK_DATA_KEY] is None
        assert m._block_queue.nodes[hash(b3)][Miner._QUEUE_BLOCK_DATA_KEY] is not None

        assert m.get_genesis_block() == hash(b1)
        assert m.get_mined_blocks() == {hash(b2), hash(b3)}

    def test_cascade_queue(self):
        net = Network()
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)

        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        m.set_network(net)
        m.set_genesis_block(b1)
        m.set_refer_handler(SimpleRef)

        b2 = m.mine_block()
        b3 = m.mine_block()
        b4 = m.mine_block()

        assert m.get_mined_blocks() == {hash(b2), hash(b3), hash(b4)}
        assert len(m._blockdag) == 4
        assert len(m._block_queue) == 0

        m._blockdag.cut_block(hash(b2))
        assert len(m._blockdag) == 1

        m.add_block(b3)
        assert len(m._blockdag) == 1
        assert len(m._block_queue) == 2

        m.add_block(b4)
        assert len(m._blockdag) == 1
        assert len(m._block_queue) == 3

        m.add_block(b2)
        assert len(m._blockdag) == 4
        assert len(m._block_queue) == 0

