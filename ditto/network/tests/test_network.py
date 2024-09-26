from ditto.blockdag import BlockDAG, BlockType, Block
from ditto.network import NetOperator
from ditto.nodes import Miner
from ditto.nodes.reference import LeavesRef
from ditto.nodes.consensus import CCC


class TestNetwork:

    def test_send(self):
        net = NetOperator(BlockDAG())
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
        assert net._total_blockdag.add_block(b1) is True

        m1 = Miner(name='testMiner1', blockdag=BlockDAG(), max_peer_num=10)
        m1.pre_launch(b1, LeavesRef, CCC)
        m2 = Miner(name='testMiner2', blockdag=BlockDAG(), max_peer_num=10)
        m2.pre_launch(b1, LeavesRef, CCC)

        net.add_miner(m1)
        net.add_miner(m2)

        assert m1.connect_peer(m2.name, 5.0) is True
        assert m2.get_neighbors() == {"testMiner1"}

        assert hash(m1.mine_block()) == 2
        assert len(m2._blockdag) == 2

    def test_mine(self):
        net = NetOperator(BlockDAG())
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
        assert net._total_blockdag.add_block(b1) is True

        m1 = Miner(name='testMiner1', blockdag=BlockDAG(), max_peer_num=10)
        m1.pre_launch(b1, LeavesRef, CCC)
        m2 = Miner(name='testMiner2', blockdag=BlockDAG(), max_peer_num=10)
        m2.pre_launch(b1, LeavesRef, CCC)

        net.add_miner(m1)
        net.add_miner(m2)

        assert hash(m1.mine_block()) == 2
        assert hash(m2.mine_block()) == 3
        assert len(net._total_blockdag) == 3
        assert len(m1._blockdag) == 2
        assert len(m2._blockdag) == 2

        assert m1.connect_peer(m2.name, 5.0) is True

        assert hash(m1.mine_block()) == 4
        assert m1._blockdag.graph().nodes().keys() == {1, 2, 4}
        assert m2._blockdag.graph().nodes().keys() == {1, 2, 3, 4}
        assert m2._blockdag.subgraph(4).nodes().keys() == {1, 2, 4}
        assert m2._blockdag.subgraph(3).nodes().keys() == {1, 3}

        assert hash(m2.mine_block()) == 5
        assert len(m1._blockdag) == 5
        assert len(m2._blockdag) == 5

    def test_three_miners(self):
        net = NetOperator(BlockDAG())
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
        assert net._total_blockdag.add_block(b1) is True

        m1 = Miner(name='testMiner1', blockdag=BlockDAG(), max_peer_num=10)
        m1.pre_launch(b1, LeavesRef, CCC)
        m2 = Miner(name='testMiner2', blockdag=BlockDAG(), max_peer_num=10)
        m2.pre_launch(b1, LeavesRef, CCC)
        m3 = Miner(name='testMiner3', blockdag=BlockDAG(), max_peer_num=10)
        m3.pre_launch(b1, LeavesRef, CCC)

        net.add_miner(m1)
        net.add_miner(m2)
        net.add_miner(m3)

        assert hash(m1.mine_block()) == 2
        assert hash(m2.mine_block()) == 3
        assert hash(m3.mine_block()) == 4

        assert m1.connect_peer(m2.name, 5.0) is True

        assert hash(m1.mine_block()) == 5
        assert m1._blockdag.graph().nodes().keys() == {1, 2, 5}
        assert len(m2._blockdag) == 4

        assert m1.connect_peer(m3.name, 5.0) is True

        assert hash(m2.mine_block()) == 6
        assert m2._blockdag.graph().nodes().keys() == {1, 2, 3, 5, 6}
        assert len(m1._blockdag) == 5

        assert len(m3._blockdag) == 6
        assert m3._blockdag.graph().nodes().keys() == {1, 2, 3, 4, 5, 6}

        print("\n" + repr(net._total_blockdag))

