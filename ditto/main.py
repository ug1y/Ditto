from ditto.blockdag import BlockDAG, DAGType
from ditto.network import NetOperator
from ditto.nodes import Miner
from ditto.nodes import ChainRef, NakamotoCons

if __name__ == '__main__':
    net = NetOperator(BlockDAG(DAGType.CONVERGENCE))
    b1 = net.init_network().pop()

    m1 = Miner(name='testMiner1', blockdag=BlockDAG(DAGType.CONVERGENCE), max_peer_num=10)
    m1.pre_launch(b1, ChainRef, NakamotoCons)
    m2 = Miner(name='testMiner2', blockdag=BlockDAG(DAGType.CONVERGENCE), max_peer_num=10)
    m2.pre_launch(b1, ChainRef, NakamotoCons)
    m3 = Miner(name='testMiner3', blockdag=BlockDAG(DAGType.CONVERGENCE), max_peer_num=10)
    m3.pre_launch(b1, ChainRef, NakamotoCons)

    net.add_miner(m1)
    net.add_miner(m2)
    net.add_miner(m3)

    m1.mine_block()  # b2 for m1
    m2.mine_block()  # b3 for m2
    m3.mine_block()  # b4 for m3

    m1.connect_peer(m2.get_name(), 5.0)
    m2.mine_block()  # b5 for m2

    m2.connect_peer(m3.get_name(), 5.0)
    m3.mine_block()  # b6 for m3

    m3.mine_block()  # b7 for m3

    m2.mine_block()  # b8 for m2

    print("\n=== testMiner1 ===")
    print(repr(m1.blockdag))
    print("sort: " + str(m1.consus_handler.sort_finished_blocks()))
    print("decided: " + str(m1.consus_handler.get_decided_blocks()))

    print("\n=== testMiner2 ===")
    print(repr(m2.blockdag))
    print("sort: " + str(m2.consus_handler.sort_finished_blocks()))
    print("decided: " + str(m2.consus_handler.get_decided_blocks()))

    print("\n=== testMiner3 ===")
    print(repr(m3.blockdag))
    print("sort: " + str(m3.consus_handler.sort_finished_blocks()))
    print("decided: " + str(m3.consus_handler.get_decided_blocks()))


