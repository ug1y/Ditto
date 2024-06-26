from ditto.blockdag import BlockDAG, BlockType, Block
from ditto.network import NetOperator
from ditto.nodes import Miner, SimpleRef, CCC, RRR


class TestMiner:

    def test_init(self):
        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        assert m._name == 'testMiner'
        assert len(m.blockdag) == 0
        assert m.max_peer_num == 10
        assert m._genesis_block == 0
        assert m._network is None
        assert len(m._mined_blocks) == 0
        assert len(m._block_queue) == 0
        assert m._refer_handler is None
        assert m._consus_handler is None

    def test_mine_block(self):
        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        assert m.mine_block() is None

        net = NetOperator(BlockDAG())
        m.set_network(net)
        assert m.mine_block() is None

        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
        m.set_genesis_block(b1)
        assert len(m.blockdag) == 1
        assert m.get_genesis_block() == 1
        assert m.mine_block() is None

        m.set_refer_handler(RRR)
        assert m.mine_block() is None

        m.set_consus_handler(CCC)
        m.set_refer_handler(SimpleRef)

        b2 = m.mine_block()
        assert len(m.blockdag) == 2
        assert hash(b2) in m

        b3 = m.mine_block()
        assert len(m.blockdag) == 3
        assert hash(b3) in m

    def test_queue_block(self):
        net = NetOperator(BlockDAG())
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)

        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        m.pre_launch(b1, SimpleRef, CCC, net)

        b2 = m.mine_block()
        b3 = m.mine_block()
        m.blockdag.cut_block(hash(b2))

        m.add_block(b3)
        assert m._block_queue.nodes.keys() == {hash(b2), hash(b3)}
        assert m._block_queue.edges.keys() == {(hash(b3), hash(b2))}
        assert m._block_queue.nodes[hash(b2)][Miner._QUEUE_BLOCK_DATA_KEY] is None
        assert m._block_queue.nodes[hash(b3)][Miner._QUEUE_BLOCK_DATA_KEY] is not None

        assert m.get_genesis_block() == hash(b1)
        assert m.get_mined_blocks() == {hash(b2), hash(b3)}

    def test_cascade_queue(self):
        net = NetOperator(BlockDAG())
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)

        m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
        m.pre_launch(b1, SimpleRef, CCC, net)

        b2 = m.mine_block()
        b3 = m.mine_block()
        b4 = m.mine_block()

        assert m.get_mined_blocks() == {hash(b2), hash(b3), hash(b4)}
        assert len(m.blockdag) == 4
        assert len(m._block_queue) == 0

        m.blockdag.cut_block(hash(b2))
        assert len(m.blockdag) == 1

        m.add_block(b3)
        assert len(m.blockdag) == 1
        assert len(m._block_queue) == 2

        m.add_block(b4)
        assert len(m.blockdag) == 1
        assert len(m._block_queue) == 3

        m.add_block(b2)
        assert len(m.blockdag) == 4
        assert len(m._block_queue) == 0

    def test_peer_process(self):
        net = NetOperator(BlockDAG())
        m1 = Miner(name='testMiner1', blockdag=BlockDAG(), max_peer_num=10)
        m2 = Miner(name='testMiner2', blockdag=BlockDAG(), max_peer_num=10)
        m3 = Miner(name='testMiner3', blockdag=BlockDAG(), max_peer_num=10)
        m4 = Miner(name='testMiner4', blockdag=BlockDAG(), max_peer_num=10)
        m5 = Miner(name='testMiner5', blockdag=BlockDAG(), max_peer_num=10)

        delay = net.get_delay(m1.get_name(), m2.get_name())

        net.add_miner(m1)
        # m1.set_network(net)

        assert m1.connect_peer(m2.get_name(), delay) is False
        net.add_miner(m2)
        assert m1.connect_peer(m2.get_name(), delay) is True

        # assert m2.connect_peer(m1.get_name(), delay) is False
        # m2.set_network(net)
        assert m2.connect_peer(m1.get_name(), delay) is True

        net.add_miner(m3)
        # m3.set_network(net)

        net.add_miner(m4)
        # m4.set_network(net)

        net.add_miner(m5)
        # m5.set_network(net)

        assert m1.discover_peer() == 3
        assert m2.discover_peer() == 3

        assert m3.discover_peer() == 2
        assert m4.discover_peer() == 1

        m5.remove_peer(m1.get_name())
        assert len(net.network_graph.edges) == 9

        print(str(net) + "\n" + repr(net))
