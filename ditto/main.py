from ditto.blockdag import Block, BlockType, BlockDAG, DAGType
from ditto.network import Network
from ditto.nodes import Miner
from ditto.nodes import SimpleRef


if __name__ == '__main__':
    net = Network()
    b1 = Block(bid=net.get_next_block_id(), btype=BlockType.GENESIS, height=1)

    m = Miner(name='testMiner', blockdag=BlockDAG(), max_peer_num=10)
    m.set_network(net)
    m.set_genesis_block(b1)
    m.set_refer_handler(SimpleRef)

    b2 = m.mine_block()
    b3 = m.mine_block()
    b4 = m.mine_block()

    m._blockdag.cut_block(hash(b2))
    m.add_block(b3)
    m.add_block(b4)
    print(m.get_mined_blocks())
    print(m._block_queue)

    m.add_block(b2)
    print(m._blockdag)
    print(m._block_queue)
