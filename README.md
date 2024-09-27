# Ditto

A hybrid blockDAG simulation framework, where the blockDAG is the directed acyclic graph-based (DAG-based) 
blockchain. This framework can interactively display the blockDAG generation, consensus protocol execution, 
and byzantine attack effect. The project is named `Ditto`, a role in the Pokémon comic, implying that the 
framework can simulate various DAG-based blockchain systems.


### Targets

Inspired by the open-source projects [PHANTOM](https://github.com/AvivYaish/PHANTOM.git) and 
[py-swirld](https://github.com/Lapin0t/py-swirld.git) , our project expands the blockDAG simulation framework, 
including the following functionalities:
1. Can simulate divergence, parallel, and convergence types blockDAG
2. Can configure the miner's behaviors, let the convergence type blockDAG degenerate into the single chain structure 
   of Nakamoto consensus (i.e. simulate Bitcoin system)
3. Can simulate various byzantine attacks against blockDAG, including selfish attacks, eclipse attacks
4. Can set special transactions in blocks, such as repeated transactions, conflicted transactions, and current version leave empty
5. Can control block generation speed, organize blocks by height, and friendly interactive visualization


### Dependencies

The project supports `python>=3.10` programming language, and depends on the following libraries:
- networkx==3.3.0  # complex network analysis library
- numpy==1.26.0  # mathematical library for computing Poisson distribution
- simpy==4.1.0  # discrete event simulation framework library based on processes
- bokeh==3.5.0  # interactive visualization library for browser
- click==8.1.7  # interactive command line interface library


### Installation

Clone the repository and execute the following commands to install the project.
```shell
git clone https://github.com/ug1y/Ditto.git
cd Ditto
pip install .
```

If you want to develop based on the current project, install it in the following way.
```shell
git clone https://github.com/ug1y/Ditto.git
cd Ditto
pip install -e .
```


### Usage

The entrance method is `ditto.main`, option `--help` for more details, and option `--version` for version information.
```shell
python -m ditto.main --help
python -m ditto.main --version
```

The project has three run modes, use `--help` to show parameters descriptions.

1. Run a simulation with the given parameters:
```shell
python -m ditto.main simu -n [net_template] -c [cons_method] \
                          -s [scale] -r [rate] -i [interval] -d [delay] \
                          -u [until] 
```

2. Run a bokeh server with the given port:
```shell
python -m ditto.main serv -p [port]
```

3. Run a simulation in the attack mode:
```shell
python -m ditto.main attk -n [net_template] -c [cons_method] \
                          -s [scale] -r [rate] -i [interval] -d [delay] \
                          -u [until] -t [times] -p [power]
```
