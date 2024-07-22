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
import logging

from bokeh.document import Document
from bokeh.plotting import figure, curdoc
from bokeh.models import (Button, Select, NumericInput, Toggle, Slider, TextAreaInput, WheelZoomTool, PanTool,
                          SingleIntervalTicker, LinearAxis, FixedTicker)
from bokeh.server.callbacks import PeriodicCallback

from ditto import config, __version__
from ditto.simulation import Simulator
from ditto.network import NetOperator, NetFactory
from ditto.blockdag import DAGType
from ditto.nodes import ChainRef, NakamotoCons

from .plots import network_plotting, blockdag_plotting
from .handler import ConsoleHandler


class PlottingApp:

    def __init__(self):
        self.network: NetOperator = None
        self.simulator: Simulator = None
        self.callfunc: PeriodicCallback = None

        self.title = "Ditto: A Hybrid BlockDAG Simulation Framework"
        self.version = __version__

        self.dag_figure = figure(name="blockdag", sizing_mode='stretch_both',
                                 tools=['wheel_zoom', 'pan', 'reset'],
                                 active_drag='pan', active_scroll='wheel_zoom')
        self.dag_figure.select_one(PanTool).dimensions = "width"
        self.dag_figure.yaxis.visible = False
        self.dag_figure.ygrid.visible = False
        self.dag_figure.xaxis.ticker = SingleIntervalTicker(interval=1)
        self.dag_figure.xaxis.minor_tick_line_color = None

        self.net_figure = figure(name="network", sizing_mode='stretch_both',
                                 tools=['wheel_zoom', 'pan', 'reset'],
                                 active_drag='pan', active_scroll='wheel_zoom')
        self.net_figure.axis.visible = False

        self.con_input = TextAreaInput(name="console", sizing_mode='stretch_both')

        options = ["Bitcoin"]
        self.sys_select = Select(name="system", title="Choose System", height=50,
                                 options=options, sizing_mode='stretch_width')
        self.sys_select.value = options[0]

        self.num_input = NumericInput(name="number", title="Network Scale", height=50,
                                      low=1, high=100, sizing_mode='stretch_width')
        self.num_input.value = 6

        self.rate_input = NumericInput(name="rate", title="Block Creation Rate", height=50,
                                       low=0, mode="float", sizing_mode='stretch_width')
        self.rate_input.value = 10.0

        self.delay_input = NumericInput(name="delay", title="Propagation Delay", height=50,
                                        low=0, mode="float", sizing_mode='stretch_width')
        self.delay_input.value = 5.0

        self.gen_button = Button(name="generate", label="Generate Network", sizing_mode='stretch_width',
                                 button_type="primary", height=45)
        self.gen_button.on_click(self.gen_click_event)

        self.run_toggle = Toggle(name="running", label="▶ Run", sizing_mode='stretch_width',
                                 button_type="success", height=45, disabled=True)
        self.run_toggle.on_change("active", self.run_change_event)

        self.speed_slider = Slider(name="speed", start=10, end=100, step=10, value=100,
                                   title="Simulation Gap(ms)", sizing_mode='stretch_width')

    def loop_simulation(self):
        consus = self.network.consus_handler
        dag = self.network.total_blockdag

        old_scale = len(dag)
        self.simulator.run(self.simulator.now + 1)
        new_scale = len(dag)

        if new_scale > old_scale:
            blockdag_plotting(self.dag_figure, dag, consus)

    def run_change_event(self, attr, old, new):
        if self.run_toggle.active:
            self.run_toggle.label = "❚❚ Pause"
            self.run_toggle.button_type = "danger"
            self.sys_select.disabled = True
            self.num_input.disabled = True
            self.gen_button.disabled = True
            self.rate_input.disabled = True
            self.delay_input.disabled = True
            self.speed_slider.disabled = True
            self.callfunc = curdoc().add_periodic_callback(self.loop_simulation, self.speed_slider.value)
            print("Run the simulation...")
        else:
            self.run_toggle.label = "▶ Run"
            self.run_toggle.button_type = "success"
            self.sys_select.disabled = False
            self.num_input.disabled = False
            self.gen_button.disabled = False
            self.rate_input.disabled = False
            self.delay_input.disabled = False
            self.speed_slider.disabled = False
            curdoc().remove_periodic_callback(self.callfunc)
            print("Pause the simulation...")

    def gen_click_event(self):
        if self.sys_select.value == "" or self.num_input.value is None or \
                self.rate_input is None or self.delay_input is None:
            print("system:", self.sys_select.value, "number:", self.num_input.value)
            return

        self.run_toggle.disabled = False
        self.con_input.value = ""

        log_filter = config.SimulatorFilter()
        log_handler = ConsoleHandler(self.con_input)
        log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s'))
        log_level = logging.INFO

        mylogger = config.MyLogger(log_handler, log_filter, log_level).getLogger()

        if self.sys_select.value == "Bitcoin":
            factory = NetFactory(mylogger)
            self.network = factory.PeerNet(blockdag_type=DAGType.CONVERGENCE, number_of_miners=self.num_input.value,
                                           reference_class=ChainRef, consensus_class=NakamotoCons,
                                           block_creation_rate=self.rate_input.value,
                                           propagation_delay_parameter=self.delay_input.value)
            self.simulator = Simulator(self.network)
            self.simulator.set_logger(mylogger)

        # Draw the network graph.
        network_plotting(self.net_figure, self.network.network_graph)
        # Draw the blockdag graph
        blockdag_plotting(self.dag_figure, self.network.total_blockdag, self.network.consus_handler)

        print("Generate a new network...")

    def modify_doc(self, doc: Document):
        doc.title = self.title
        # doc.template_variables['title'] = title  # useless code
        doc.template_variables['version'] = self.version

        doc.add_root(self.dag_figure)
        doc.add_root(self.net_figure)
        doc.add_root(self.con_input)

        doc.add_root(self.sys_select)
        doc.add_root(self.num_input)
        doc.add_root(self.rate_input)
        doc.add_root(self.delay_input)
        doc.add_root(self.gen_button)

        doc.add_root(self.run_toggle)
        doc.add_root(self.speed_slider)


# Create a new plot and add it to the document.
PlottingApp().modify_doc(curdoc())

# Use `bokeh serve --show ditto\interaction` to run the server.
