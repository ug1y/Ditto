from ditto.blockdag import Block, BlockType, BlockDAG
from ditto.network import NetOperator
from ditto.nodes import Miner
from ditto.nodes import SimpleRef, CCC

if __name__ == '__main__':
    net = NetOperator(BlockDAG())
    b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
    net.total_blockdag.add_block(b1)

    m1 = Miner(name='testMiner1', blockdag=BlockDAG(), max_peer_num=10)
    m1.pre_launch(b1, SimpleRef, CCC)
    m2 = Miner(name='testMiner2', blockdag=BlockDAG(), max_peer_num=10)
    m2.pre_launch(b1, SimpleRef, CCC)

    net.add_miner(m1)
    net.add_miner(m2)

    # m1.connect_peer(m2.get_name(), 5.0)
    # print(m2.get_neighbors())
    m1.mine_block()
    m1.mine_block()

    m1.connect_peer(m2.get_name(), 5.0)

    m2.mine_block()
    m1.mine_block()

    print(repr(net.total_blockdag))
    print(repr(m1), m2._block_queue.nodes.keys())
    print(repr(m2), m2._block_queue.nodes.keys())

