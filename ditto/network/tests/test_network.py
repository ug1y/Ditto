from ditto.blockdag import BlockDAG, BlockType, Block
from ditto.network import NetOperator
from ditto.nodes import Miner, SimpleRef, CCC


class TestNetwork:

    def test_send(self):
        net = NetOperator(BlockDAG())
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
        assert net.total_blockdag.add_block(b1) is True

        m1 = Miner(name='testMiner1', blockdag=BlockDAG(), max_peer_num=10)
        m1.pre_launch(b1, SimpleRef, CCC)
        m2 = Miner(name='testMiner2', blockdag=BlockDAG(), max_peer_num=10)
        m2.pre_launch(b1, SimpleRef, CCC)

        net.add_miner(m1)
        net.add_miner(m2)

        assert m1.connect_peer(m2.get_name(), 5.0) is True
        assert m2.get_neighbors() == {"testMiner1"}

        assert hash(m1.mine_block()) == 2
        assert len(m2.blockdag) == 2

    def test_mine(self):
        net = NetOperator(BlockDAG())
        b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
        assert net.total_blockdag.add_block(b1) is True

        m1 = Miner(name='testMiner1', blockdag=BlockDAG(), max_peer_num=10)
        m1.pre_launch(b1, SimpleRef, CCC)
        m2 = Miner(name='testMiner2', blockdag=BlockDAG(), max_peer_num=10)
        m2.pre_launch(b1, SimpleRef, CCC)

        net.add_miner(m1)
        net.add_miner(m2)

        assert hash(m1.mine_block()) == 2
        assert hash(m2.mine_block()) == 3
        assert len(net.total_blockdag) == 3
        assert len(m1.blockdag) == 2
        assert len(m2.blockdag) == 2

        assert m1.connect_peer(m2.get_name(), 5.0) is True

        assert hash(m1.mine_block()) == 4
        assert len(m1.blockdag) == 3
        assert len(m2.blockdag) == 4

        assert hash(m2.mine_block()) == 5
        assert len(m1.blockdag) == 5
        assert len(m2.blockdag) == 5

        print(repr(net.total_blockdag))