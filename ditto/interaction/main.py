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
from bokeh.models import Button, GraphRenderer, Circle, StaticLayoutProvider, ColumnDataSource, MultiLine, LabelSet
from bokeh.plotting import figure, curdoc

from ditto.blockdag import DAGType
from ditto.network import PeerNet
from ditto.nodes import ChainRef, NakamotoCons

import networkx as nx


class PlottingApp:

    def __init__(self):
        self.title = "Ditto: A Hybrid BlockDAG Simulation Framework"
        self.version = "0.1.0"

        self.dag_plot = figure(name="blockdag", sizing_mode='stretch_both')
        self.button = Button(name="button", label="click me", button_type="success")
        self.net_plot = figure(name="network", sizing_mode='stretch_both', x_range=(-10, 10),
                               y_range=(-10, 10))

    def network_plotting(self):
        peernet = PeerNet(blockdag_type=DAGType.CONVERGENCE,
                          number_of_miners=5,
                          reference_class=ChainRef,
                          consensus_class=NakamotoCons,
                          block_creation_rate=10.0,
                          propagation_delay_parameter=30.0)

        net_graph = peernet.network_graph

        renderer = GraphRenderer()

        node_data_src = ColumnDataSource({
            'index': list(net_graph.nodes)})
        renderer.node_renderer.data_source = node_data_src
        renderer.node_renderer.glyph = Circle(radius=1, fill_color="blue")

        edge_data_src = ColumnDataSource({
            'start': [e[0] for e in net_graph.edges()],
            'end': [e[1] for e in net_graph.edges()]})
        renderer.edge_renderer.data_source = edge_data_src
        renderer.edge_renderer.glyph = MultiLine(line_color="grey", line_width=2)

        layout = nx.spring_layout(net_graph, scale=8)
        renderer.layout_provider = StaticLayoutProvider(graph_layout=layout)

        self.net_plot.renderers.clear()
        self.net_plot.renderers.append(renderer)

        labels = LabelSet(x='x', y='y', text='text', level='glyph', x_offset=5, y_offset=5,
                          source=ColumnDataSource({'x': [m[0] for m in layout.values()],
                                                   'y': [m[1] for m in layout.values()],
                                                   'text': [m for m in layout.keys()]}))
        self.net_plot.center.clear()
        self.net_plot.add_layout(labels, 'center')

    def modify_doc(self, doc: Document):
        doc.title = self.title
        # doc.template_variables['title'] = title  # useless code
        doc.template_variables['version'] = self.version

        self.dag_plot.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])

        # self.button.on_event("button_click", lambda: print("click!"))
        self.button.on_event("button_click", self.network_plotting)

        doc.add_root(self.dag_plot)
        doc.add_root(self.button)
        doc.add_root(self.net_plot)


# Create a new plot and add it to the document.
PlottingApp().modify_doc(curdoc())

# Use `bokeh serve --show ditto\interaction` to run the server.
