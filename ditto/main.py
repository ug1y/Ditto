import logging
import os
import sys

from ditto import config
from ditto.network import NetFactory, SelectNetTemplate
from ditto.nodes import Systems, StatusType
from ditto.simulation import Simulator


def run_simulation(until: int = 100):
    log_filter = config.SimulatorFilter()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(message)s'))
    log_level = logging.INFO

    mylogger = config.MyLogger(log_handler, log_filter, log_level).getLogger()

    factory = NetFactory(mylogger)
    system_params = Systems['ULBlockDAG']
    net = SelectNetTemplate(factory, net_name='PeerNet', system_params=system_params, number_of_miners=5,
                            block_creation_rate=10, propagation_delay_parameter=30)

    sim = Simulator(net)
    sim.set_logger(mylogger)
    sim.run(until)

    print(repr(net.total_blockdag))

    if net.consus_handler is not None:
        print(net.consus_handler.get_processed_blocks(StatusType.DECIDED))
        print(net.consus_handler.sort_finished_blocks())
        print(net.consus_handler.block_status(5))
        print(net.consus_handler.block_status(10))
        print(net.consus_handler.block_status(15))


def run_server(port: int = 5006):
    print('Opening Bokeh application on http://localhost:' + str(port) + '/')
    os.environ['PYTHONPATH'] = os.getcwd()  # Add the current working directory to the PYTHONPATH
    os.system('bokeh serve --show ' + os.path.join('ditto', 'interaction') + ' --port ' + str(port))


if __name__ == '__main__':
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
