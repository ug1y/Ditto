from ditto.blockdag import Block, BlockType, BlockDAG
from ditto.network import NetOperator
from ditto.nodes import Miner
from ditto.nodes import SimpleRef, CCC

if __name__ == '__main__':
    net = NetOperator(BlockDAG())
    b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)
    net.total_blockdag.add_block(b1)

    m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
    net.add_miner(m)

    m.pre_launch(b1, SimpleRef, CCC)
    print(m.get_genesis_block())

    b2 = m.mine_block()
    b3 = m.mine_block()
    b4 = m.mine_block()

    print(str(m) + "\n" + repr(m))
