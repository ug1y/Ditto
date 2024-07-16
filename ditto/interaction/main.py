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
from bokeh.models import (Button, GraphRenderer, Circle, StaticLayoutProvider, ColumnDataSource,
                          MultiLine, LabelSet, Select, NumericInput, Toggle, Slider)

from ditto.simulation import Simulator
from ditto.network import NetOperator, PeerNet
from ditto.blockdag import DAGType
from ditto.nodes import ChainRef, NakamotoCons

import networkx as nx


class PlottingApp:

    def __init__(self):
        self.network: NetOperator = None
        self.simulator: Simulator = None

        self.title = "Ditto: A Hybrid BlockDAG Simulation Framework"
        self.version = "0.1.0"

        self.dag_figure = figure(name="blockdag", sizing_mode='stretch_both')

        options = ["Bitcoin"]
        self.sys_select = Select(name="system", options=options, sizing_mode='stretch_width')

        self.num_input = NumericInput(name="number", low=1, high=100, sizing_mode='stretch_width')

        self.gen_button = Button(name="generate", label="Generate Network", sizing_mode='stretch_width',
                                 button_type="primary", height=40)
        self.gen_button.on_click(self.gen_click_event)

        self.run_toggle = Toggle(name="running", label="Run", sizing_mode='stretch_width',
                                 button_type="success", height=120)
        self.run_toggle.on_change("active", self.run_change_event)

        self.rate_input = NumericInput(name="rate", low=0, mode="float",
                                       title="Block Creation Rate:", sizing_mode='stretch_width')

        self.delay_input = NumericInput(name="delay", low=0, mode="float",
                                        title="Propagation Delay:", sizing_mode='stretch_width')

        self.speed_slider = Slider(name="speed", start=1, end=10, step=1, value=1,
                                   title="Simulation Speed", sizing_mode='stretch_width')

        self.net_figure = figure(name="network", sizing_mode='stretch_both',
                                 x_range=(-20, 20), y_range=(-20, 20))

    def run_change_event(self, attr, old, new):
        if self.run_toggle.active:
            self.run_toggle.label = "Pause"
            self.run_toggle.button_type = "danger"
            self.sys_select.disabled = True
            self.num_input.disabled = True
            self.gen_button.disabled = True
            self.rate_input.disabled = True
            self.delay_input.disabled = True
            self.speed_slider.disabled = True
        else:
            self.run_toggle.label = "Run"
            self.run_toggle.button_type = "success"
            self.sys_select.disabled = False
            self.num_input.disabled = False
            self.gen_button.disabled = False
            self.rate_input.disabled = False
            self.delay_input.disabled = False
            self.speed_slider.disabled = False

    def gen_click_event(self):
        if self.sys_select.value == "" or self.num_input.value is None:
            print("system:", self.sys_select.value, "number:", self.num_input.value)
            return

        if self.sys_select.value == "Bitcoin":
            number = self.num_input.value
            self.rate_input.value = 10.0
            self.delay_input.value = 30.0
            self.network = PeerNet(blockdag_type=DAGType.CONVERGENCE, number_of_miners=number,
                                   reference_class=ChainRef, consensus_class=NakamotoCons,
                                   block_creation_rate=self.rate_input.value,
                                   propagation_delay_parameter=self.delay_input.value)

            # Draw the network graph.
            self.network_plotting(self.network.network_graph)

    def network_plotting(self, graph: nx.DiGraph):
        # Use GraphRenderer to draw the network graph.
        renderer = GraphRenderer()

        # Setting node data and glyph.
        renderer.node_renderer.data_source = ColumnDataSource({
            'index': list(graph.nodes)})
        renderer.node_renderer.glyph = Circle(radius=1, fill_color="green")

        # Setting edge data and glyph.
        renderer.edge_renderer.data_source = ColumnDataSource({
            'start': [e[0] for e in graph.edges()],
            'end': [e[1] for e in graph.edges()]})
        renderer.edge_renderer.glyph = MultiLine(line_color="grey", line_width=2)

        # Using the spring layout to display the graph.
        layout = nx.spring_layout(graph, scale=16)
        renderer.layout_provider = StaticLayoutProvider(graph_layout=layout)

        # Refresh the figure.
        self.net_figure.renderers.clear()
        self.net_figure.renderers.append(renderer)

        # Add labels.
        labels = LabelSet(x='x', y='y', text='text', level='glyph', x_offset=5, y_offset=5,
                          source=ColumnDataSource({'x': [m[0] for m in layout.values()],
                                                   'y': [m[1] for m in layout.values()],
                                                   'text': [m for m in layout.keys()]}))
        labels.text_font_size = '8pt'
        # Refresh the labels.
        self.net_figure.center.clear()
        self.net_figure.add_layout(labels, 'center')

    def modify_doc(self, doc: Document):
        doc.title = self.title
        # doc.template_variables['title'] = title  # useless code
        doc.template_variables['version'] = self.version

        self.dag_figure.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])

        doc.add_root(self.dag_figure)
        doc.add_root(self.sys_select)
        doc.add_root(self.num_input)
        doc.add_root(self.gen_button)
        doc.add_root(self.run_toggle)
        doc.add_root(self.net_figure)
        doc.add_root(self.rate_input)
        doc.add_root(self.delay_input)
        doc.add_root(self.speed_slider)


# Create a new plot and add it to the document.
PlottingApp().modify_doc(curdoc())

# Use `bokeh serve --show ditto\interaction` to run the server.
