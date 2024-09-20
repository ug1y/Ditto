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

from ditto import runs, __version__

banner = """
           __    _    __     __         
      ____/ /   (_)  / /_   / /_   ____ 
     / __  /   / /  / __/  / __/  / __ \\
    / /_/ /   / /  / /_   / /_   / /_/ /
    \__,_/   /_/   \__/   \__/   \____/
"""


@click.version_option(version=__version__)
@click.group()
def cli():
    click.echo(f">>> Ditto: A Hybrid BlockDAG Simulation Framework <<<")
    click.echo(banner)


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
def simu(net_template, cons_method, scale, rate, delay, until):
    """ Run a simulation with the given parameters. """
    # click.echo(f"Run simulation with the following parameters:")
    # click.echo(f"(Network='{net}', Consensus='{cons}', Scale='{scale}', Rate='{rate}', Delay='{delay}')")
    click.echo(f"Simulation will run until '{until}' sim times.")
    runs.run_simulation(until, net_template, cons_method, scale, rate, delay)


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
