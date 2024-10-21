#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2024 Hao Yin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import click

from ditto import runs

__banner__ = """
           __    _    __     __         
      ____/ /   (_)  / /_   / /_   ____ 
     / __  /   / /  / __/  / __/  / __ \\
    / /_/ /   / /  / /_   / /_   / /_/ /
    \__,_/   /_/   \__/   \__/   \____/
"""
__title__ = "Ditto: A Hybrid BlockDAG Simulation Framework"
__version__ = '0.7.1'


@click.version_option(version=__version__, prog_name=__title__)
@click.group()
def cli():
    click.echo(f">>> {__title__} <<<")
    click.echo(__banner__)


@cli.command()
@click.option(
    "-n",
    "--net_template",
    type=click.Choice(['PeerNet', 'FullNet', 'RingNet', 'StarNet', 'TreeNet']),
    default="PeerNet",
    help="Specify network template, default PeerNet.",
)
@click.option(
    "-c",
    "--cons_method",
    type=click.Choice(['Nakamoto', 'Phantom', 'ULBlockDAG', 'Pikavolt']),
    default="Nakamoto",
    help="Choose consensus method, default Nakamoto.",
)
@click.option(
    "-s",
    "--scale",
    type=click.INT,
    default=6,
    help="Set network scale (miners), default 6.",
)
@click.option(
    "-r",
    "--rate",
    type=click.FLOAT,
    default=10.0,
    help="Set miner computing hash rate, default 10.0.",
)
@click.option(
    "-i",
    "--interval",
    type=click.FLOAT,
    default=10.0,
    help="Set block creation interval, default 10.0.",
)
@click.option(
    "-d",
    "--delay",
    type=click.FLOAT,
    default=30.0,
    help="Set propagation delay, default 30.0.",
)
@click.option(
    "-u",
    "--until",
    type=click.INT,
    default=1000,
    help="Run simulation until time, default 1000.",
)
@click.option(
    "-t",
    "--times",
    type=click.INT,
    default=0,
    help="Set attack times, default 0 means never stop",
)
@click.option(
    "-p",
    "--power",
    type=click.FLOAT,
    default=0.3,
    help="Set computing power ratio of the attacker, default 0.3.",
)
def attk(net_template, cons_method, scale, rate, interval, delay, until, times, power):
    """Run a simulation in the attack mode."""
    click.echo(f"Simulation will run until '{until}' sim times or attack until {times} times.")
    runs.run_with_attack(net_template, cons_method, scale, rate, interval, delay, until, times, power)
    print(f"Function 'run_with_attack' took '{runs.run_with_attack.last_elapsed_time:.3f}' seconds to execute.")


@cli.command()
@click.option(
    "-n",
    "--net_template",
    type=click.Choice(['PeerNet', 'FullNet', 'RingNet', 'StarNet', 'TreeNet']),
    default="PeerNet",
    help="Specify network template, default PeerNet.",
)
@click.option(
    "-c",
    "--cons_method",
    type=click.Choice(['Nakamoto', 'Phantom', 'ULBlockDAG', 'Pikavolt']),
    default="Nakamoto",
    help="Choose consensus method, default Nakamoto.",
)
@click.option(
    "-s",
    "--scale",
    type=click.INT,
    default=6,
    help="Set network scale (miners), default 6.",
)
@click.option(
    "-r",
    "--rate",
    type=click.FLOAT,
    default=10.0,
    help="Set miner computing hash rate, default 10.0.",
)
@click.option(
    "-i",
    "--interval",
    type=click.FLOAT,
    default=10.0,
    help="Set block creation interval, default 10.0.",
)
@click.option(
    "-d",
    "--delay",
    type=click.FLOAT,
    default=30.0,
    help="Set propagation delay, default 30.0.",
)
@click.option(
    "-u",
    "--until",
    type=click.INT,
    default=100,
    help="Run simulation until time, default 100.",
)
def simu(net_template, cons_method, scale, rate, interval, delay, until):
    """ Run a simulation with the given parameters. """
    click.echo(f"Simulation will run until '{until}' sim times.")
    runs.run_simulation(net_template, cons_method, scale, rate, interval, delay, until)
    print(f"Function 'run_simulation' took '{runs.run_simulation.last_elapsed_time:.3f}' seconds to execute.")


@cli.command()
@click.option(
    "-p",
    "--port",
    type=click.INT,
    default=5006,
    help="The port number, default 5006.",
)
def serv(port):
    """ Run a bokeh server with the given port. """
    click.echo(f"Run server on port {port}")
    runs.run_server(port)


if __name__ == '__main__':
    cli()
