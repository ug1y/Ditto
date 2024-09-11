import logging
import os
import click

from ditto import config
from ditto.network import NetFactory, SelectNetTemplate
from ditto.nodes import Systems, StatusType
from ditto.simulation import Simulator

banner = """
           __    _    __     __         
      ____/ /   (_)  / /_   / /_   ____ 
     / __  /   / /  / __/  / __/  / __ \\
    / /_/ /   / /  / /_   / /_   / /_/ /
    \__,_/   /_/   \__/   \__/   \____/
"""


def run_simulation(until: int = 100, net: str = 'PeerNet', cons: str = 'Bitcoin',
                   scale: int = 6, rate: float = 10.0, delay: float = 30.0):
    log_filter = config.SimulatorFilter()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(message)s'))
    log_level = logging.INFO

    mylogger = config.MyLogger(log_handler, log_filter, log_level).getLogger()

    factory = NetFactory(mylogger)
    system_params = Systems[cons]
    net = SelectNetTemplate(factory, net_name=net, system_params=system_params, number_of_miners=scale,
                            block_creation_rate=rate, propagation_delay_parameter=delay)

    sim = Simulator(net)
    sim.set_logger(mylogger)
    sim.run(until)

    print("Simulation Done!\n")
    print(f"The simulation parameters: (Network='{net}', Consensus='{cons}', "
          f"Scale='{scale}', Rate='{rate}', Delay='{delay}')")
    print("Total blockDAG:", repr(net.total_blockdag))

    if net.consus_handler is not None:
        print("The consensus blocks set:", net.consus_handler.get_processed_blocks(StatusType.DECIDED))
        print("The finished blocks sorted:", net.consus_handler.sort_finished_blocks())


def run_server(port: int = 5006):
    print('Opening Bokeh application on http://localhost:' + str(port) + '/')
    os.environ['PYTHONPATH'] = os.getcwd()  # Add the current working directory to the PYTHONPATH
    os.system('bokeh serve --show ' + os.path.join('ditto', 'interaction') + ' --port ' + str(port))


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "-n",
    "--net",
    type=click.Choice(['PeerNet', 'FullNet', 'RingNet', 'RandomNet', 'StarNet', 'LineNet', 'TreeNet']),
    default="PeerNet",
    help="Specify network template, default PeerNet.",
)
@click.option(
    "-c",
    "--cons",
    type=click.Choice(['Bitcoin', 'Phantom', 'ULBlockDAG', 'Pikavolt']),
    default="Bitcoin",
    help="Choose simulated consensus, default Bitcoin.",
)
@click.option(
    "-s",
    "--scale",
    type=click.INT,
    default=6,
    help="Set network scale, default 6.",
)
@click.option(
    "-r",
    "--rate",
    type=click.INT,
    default=10,
    help="Set block creation rate, default 10.",
)
@click.option(
    "-d",
    "--delay",
    type=click.INT,
    default=30,
    help="Set propagation delay, default 30.",
)
@click.option(
    "-u",
    "--until",
    type=click.INT,
    default=100,
    help="Run simulation until time, default 100.",
)
def simu(net, cons, scale, rate, delay, until):
    """ Run a simulation with the given parameters. """
    # click.echo(f"Run simulation with the following parameters:")
    # click.echo(f"(Network='{net}', Consensus='{cons}', Scale='{scale}', Rate='{rate}', Delay='{delay}')")
    click.echo(f"Simulation will run until '{until}' sim times.")
    run_simulation(until, net, cons, scale, rate, delay)


@cli.command()
@click.option(
    "-p",
    "--port",
    type=click.INT,
    default=5006,
    help="The port number (default 5006).",
)
def serv(port):
    """ Run a bokeh server with the given port. """
    click.echo(f"Run server on port {port}")
    run_server(port)


if __name__ == '__main__':
    click.echo(f">>> Ditto: A Hybrid BlockDAG Simulation Framework <<<")
    click.echo(banner)
    cli()
