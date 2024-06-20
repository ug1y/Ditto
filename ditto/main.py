from ditto.blockdag import Block, BlockType, BlockDAG, DAGType
from ditto.network import Network
from ditto.nodes import Miner


if __name__ == '__main__':
    net = Network()
    m1 = Miner(name='test', blockdag=BlockDAG(gtype=DAGType.DIVERGENCE), max_peer_num=10)
    m1.set_network(net)
    print(str(m1) + "\n" + repr(m1))
    print(m1.get_genesis_block() in m1)

    b1 = Block(bid=net.get_next_block_id(), type=BlockType.GENESIS, height=1)
    m1.set_genesis_block(b1)
    print(str(m1) + "\n" + repr(m1))
    print(m1.get_genesis_block() in m1)

    print(m1.get_mined_blocks())
    m1.send_block(receiver='test', bid=m1.get_genesis_block())
    print(m1.mine_block())

    b3 = m1.mine_block()
    m1.add_block(b3)
    print(str(m1) + "\n" + repr(m1))