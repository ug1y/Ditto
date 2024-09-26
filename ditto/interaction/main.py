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
from bokeh.document import Document
from bokeh.plotting import figure, curdoc
from bokeh.models import Button, Select, Toggle, Slider, NumericInput, TextAreaInput
from bokeh.models import Div, PanTool, SingleIntervalTicker
from bokeh.server.callbacks import PeriodicCallback

from ditto import config
from ditto.main import __title__, __version__
from ditto.simulation import Simulator, StatsRecorder
from ditto.network import NetOperator, NetFactory
from ditto.nodes import Systems

from ditto.interaction.plots import network_plotting, blockdag_plotting
from ditto.interaction.param import ConsoleHandler, SystemRef, ParamsConfig


class PlottingApp:

    def __init__(self):
        self.network: NetOperator = None
        self.simulator: Simulator = None
        self.recorder: StatsRecorder = None
        self.callfunc: PeriodicCallback = None

        self.title = __title__
        self.version = __version__

        # BlockDAG presentation.
        self.dag_figure = figure(name="blockdag", sizing_mode='stretch_both', tools=['wheel_zoom', 'pan', 'reset'],
                                 active_drag='pan', active_scroll='wheel_zoom')
        self.dag_figure.select_one(PanTool).dimensions = "width"
        self.dag_figure.yaxis.visible = False
        self.dag_figure.ygrid.visible = False
        self.dag_figure.xaxis.ticker = SingleIntervalTicker(interval=1)
        self.dag_figure.xaxis.minor_tick_line_color = None

        # Network presentation.
        self.net_figure = figure(name="network", sizing_mode='stretch_both', tools=['wheel_zoom', 'pan', 'reset'],
                                 active_drag='pan', active_scroll='wheel_zoom')
        self.net_figure.axis.visible = False

        # Logger output area.
        self.con_input = TextAreaInput(name="console", sizing_mode='stretch_both')

        # Statistics presentation.
        self.stats_div = Div(name="stats", sizing_mode='stretch_both', styles={'font-size': '14px'})

        # Interactively control area.
        sys_options = ["Nakamoto", "Phantom", "ULBlockDAG", "Pikavolt"]
        self.sys_select = Select(name="system", title="Choose System", height=50,
                                 options=sys_options, sizing_mode='stretch_width')
        self.sys_select.value = sys_options[0]
        self.sys_select.on_change('value', self.sys_change_event)

        self.link_div = Div(name="link", height=50, sizing_mode='stretch_both',
                            styles={'text-align': 'center'})

        self.num_input = NumericInput(name="number", title="Network Scale", height=50,
                                      low=1, high=100, sizing_mode='stretch_width')

        self.interval_input = NumericInput(name="interval", title="Block Creation Interval", height=50,
                                           low=0, mode="float", sizing_mode='stretch_width')

        self.delay_input = NumericInput(name="delay", title="Propagation Delay", height=50,
                                        low=0, mode="float", sizing_mode='stretch_width')

        net_options = ["PeerNet", "FullNet", "RingNet", "StarNet", "TreeNet"]
        self.net_select = Select(name="net_name", title="Select Network", height=50,
                                 options=net_options, sizing_mode='stretch_width')
        self.net_select.value = net_options[0]

        self.gen_button = Button(name="generate", label="Generate Network", sizing_mode='stretch_width',
                                 button_type="primary", height=50)
        self.gen_button.on_click(self.gen_click_event)

        self.run_toggle = Toggle(name="running", label="▶ Run", sizing_mode='stretch_width',
                                 button_type="success", height=50, disabled=True)
        self.run_toggle.on_change("active", self.run_change_event)

        self.speed_slider = Slider(name="speed", start=10, end=100, step=10, value=100,
                                   title="Simulation Gap(ms)", sizing_mode='stretch_width')

        # Init the input widgets.
        self.sys_change_event(None, None, None)

    def loop_simulation(self):
        consus = self.network.consus_handler
        dag = self.network.total_blockdag

        old_scale = len(dag)
        self.simulator.run(self.simulator.env.now + 1)
        new_scale = len(dag)

        if new_scale > old_scale:
            blockdag_plotting(self.dag_figure, dag, consus)
            throughput = self.recorder.compute_throughput()
            latency = self.recorder.compute_latency()
            change_dist = self.recorder.compute_change_dist()
            self.stats_div.text = "<b>[The simulated throughput]</b> " + \
                                  f"<p>processed blocks and speed: {throughput[0][0]}, {throughput[0][1]:.2f} </p>" + \
                                  f"<p>decided blocks and speed: {throughput[1][0]}, {throughput[1][1]:.2f} </p>" + \
                                  "<br><b>[The simulated latency]</b>" + \
                                  f"<p>average latency: {latency[0]:.2f} </p>" + \
                                  "<br><b>[The simulated change distribution]</b>" + \
                                  f"<p>change index: {change_dist[0]:.2f} </p>" + \
                                  f"<p>change distribution: {change_dist[1]} </p>"

    def sys_change_event(self, attr, old, new):
        params: ParamsConfig = SystemRef[self.sys_select.value]
        self.link_div.text = ("<p>View the paper: <a href='" + params.file_path +
                              "' target='_blank'>" + params.file_name + "</a><p>")
        self.num_input.value = params.miner_number
        self.interval_input.value = params.block_interval
        self.delay_input.value = params.propagation_delay

    def run_change_event(self, attr, old, new):
        if self.run_toggle.active:
            self.run_toggle.label = "❚❚ Pause"
            self.run_toggle.button_type = "danger"
            self.sys_select.disabled = True
            self.num_input.disabled = True
            self.interval_input.disabled = True
            self.delay_input.disabled = True
            self.net_select.disabled = True
            self.gen_button.disabled = True
            self.speed_slider.disabled = True
            self.callfunc = curdoc().add_periodic_callback(self.loop_simulation, self.speed_slider.value)
            print("Run the simulation...")
        else:
            self.run_toggle.label = "▶ Run"
            self.run_toggle.button_type = "success"
            self.sys_select.disabled = False
            self.num_input.disabled = False
            self.interval_input.disabled = False
            self.delay_input.disabled = False
            self.net_select.disabled = False
            self.gen_button.disabled = False
            self.speed_slider.disabled = False
            curdoc().remove_periodic_callback(self.callfunc)
            print("Pause the simulation...")

    def gen_click_event(self):
        if self.sys_select.value == "" or self.num_input.value is None or \
                self.interval_input is None or self.delay_input is None:
            print("system:", self.sys_select.value, "number:", self.num_input.value)
            return

        self.run_toggle.disabled = False
        self.con_input.value = ""
        self.stats_div.text = ""

        mylogger = config.create_logger(ConsoleHandler(self.con_input))
        factory = NetFactory(mylogger)
        system_params = Systems[self.sys_select.value]
        self.network = factory.select_template(net_name=self.net_select.value, system_params=system_params,
                                               number_of_miners=self.num_input.value, computing_hash_rate=10.0,
                                               block_creation_interval=self.interval_input.value,
                                               propagation_delay_parameter=self.delay_input.value)
        self.simulator = Simulator(self.network)
        self.simulator.set_logger(mylogger)
        self.recorder = StatsRecorder(self.simulator, self.network.total_blockdag, self.network.consus_handler)

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
        doc.add_root(self.stats_div)

        doc.add_root(self.sys_select)
        doc.add_root(self.link_div)
        doc.add_root(self.num_input)
        doc.add_root(self.interval_input)
        doc.add_root(self.delay_input)
        doc.add_root(self.net_select)
        doc.add_root(self.gen_button)

        doc.add_root(self.run_toggle)
        doc.add_root(self.speed_slider)


# Create a new plot and add it to the document.
PlottingApp().modify_doc(curdoc())

# Use `bokeh serve --show ditto\interaction` to run the server.
