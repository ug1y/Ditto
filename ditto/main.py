import logging

from ditto.simulation import Simulator
from ditto.network import NetOperator, NetFactory
from ditto.nodes import Miner, ChainRef, NakamotoCons
from ditto.blockdag import BlockDAG, DAGType

import os, sys
from ditto import config


def run_network():
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


def run_simulation(until: int = 100):

    log_filter = config.SimulatorFilter()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s'))
    log_level = logging.INFO

    mylogger = config.MyLogger(log_handler, log_filter, log_level).getLogger()

    factory = NetFactory(mylogger)
    net = factory.PeerNet(blockdag_type=DAGType.CONVERGENCE, number_of_miners=5,
                          reference_class=ChainRef, consensus_class=NakamotoCons,
                          block_creation_rate=10, propagation_delay_parameter=0)
    sim = Simulator(net)
    sim.set_logger(mylogger)

    sim.run(until)

    for leaf in net.total_blockdag.get_leaves_blocks():
        print(net.total_blockdag.get_pivot_chain(leaf))


def run_server(port: int = 5006):
    print('Opening Bokeh application on http://localhost:' + str(port) + '/')
    os.environ['PYTHONPATH'] = os.getcwd()  # Add the current working directory to the PYTHONPATH
    os.system('bokeh serve --show ' + os.path.join('ditto', 'interaction') + ' --port ' + str(port))


if __name__ == '__main__':
    # run_network()
    # run_simulation()
    # run_server()
    if len(sys.argv) < 2:
        print('Input args like `python -m ditto.main sim [until]` or `python -m ditto.main ser [port]`')
    elif len(sys.argv) == 2:
        app = str(sys.argv[1])
        if app == 'sim':
            run_simulation()
        if app == 'ser':
            run_server()
    elif len(sys.argv) == 3:
        app, arg = str(sys.argv[1]), int(sys.argv[2])
        if app == 'sim':
            run_simulation(arg)
        if app == 'ser':
            run_server(arg)
