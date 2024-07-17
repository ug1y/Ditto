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
import networkx as nx
from bokeh.models import (GraphRenderer, ColumnDataSource, Circle, MultiLine, StaticLayoutProvider,
                          LabelSet, Range1d, Rect)
from bokeh.plotting import figure

from ditto.network import NetContainer
from ditto.blockdag import BlockDAG


def cal_loc(idx, nds, x_zoom, y_zoom):
    loc = {}
    nds = sorted(nds)
    for pos, nd in enumerate(nds):
        loc[nd] = (x_zoom * idx, y_zoom * (pos + 1) * (1 / (len(nds) + 1)))
    return loc


def blockdag_plotting(fig: figure, dag: BlockDAG):
    # Use GraphRenderer to draw the network graph.
    renderer = GraphRenderer()

    # Setting node data and glyph.
    renderer.node_renderer.data_source = ColumnDataSource({
        'index': list(dag)})
    renderer.node_renderer.glyph = Rect(width=5, height=0.5, fill_color="skyblue")

    # Update the view of the figure.
    view_n = 10
    view_x = max(len(dag.get_column_blocks()), view_n)
    fig.x_range = Range1d((view_x - view_n) * 10 - 5, view_x * 10 - 5)
    fig.y_range = Range1d(0, 10)

    # Compute the layout of the nodes.
    layout = {}
    for i, v in enumerate(dag.get_column_blocks()):
        layout.update(cal_loc(i, v, 10, 10))
    renderer.layout_provider = StaticLayoutProvider(graph_layout=layout)

    # Refresh the figure.
    fig.renderers.clear()
    fig.renderers.append(renderer)

    # Add labels for each block.
    labels_of_block = LabelSet(x='x', y='y', text='text', level='glyph', x_offset=-6, y_offset=-4,
                               source=ColumnDataSource({
                                   'x': [m[0] for m in layout.values()],
                                   'y': [m[1] for m in layout.values()],
                                   'text': [m for m in layout.keys()]}))
    labels_of_block.text_font_size = '8pt'

    # Refresh the labels.
    fig.center.clear()
    fig.add_layout(labels_of_block, 'center')


def network_plotting(fig: figure, graph: nx.Graph):
    # Use GraphRenderer to draw the network graph.
    renderer = GraphRenderer()

    # Setting node data and glyph.
    renderer.node_renderer.data_source = ColumnDataSource({
        'index': list(graph.nodes)})
    renderer.node_renderer.glyph = Circle(radius=1, fill_color="seagreen")

    # Setting edge data and glyph.
    renderer.edge_renderer.data_source = ColumnDataSource({
        'start': [e[0] for e in graph.edges()],
        'end': [e[1] for e in graph.edges()]})
    renderer.edge_renderer.glyph = MultiLine(line_color="grey", line_width=2)

    # Using the spring layout to display the graph.
    fig.x_range = Range1d(-20, 20)
    fig.y_range = Range1d(-20, 20)
    layout = nx.spring_layout(graph, scale=16)
    renderer.layout_provider = StaticLayoutProvider(graph_layout=layout)

    # Refresh the figure.
    fig.renderers.clear()
    fig.renderers.append(renderer)

    # Add labels.
    labels_for_node = LabelSet(x='x', y='y', text='text', level='glyph', x_offset=5, y_offset=5,
                               source=ColumnDataSource({
                                   'x': [m[0] for m in layout.values()],
                                   'y': [m[1] for m in layout.values()],
                                   'text': [m for m in layout.keys()]}))
    labels_for_node.text_font_size = '8pt'
    labels_for_edge = LabelSet(x='x', y='y', text='text', level='glyph',
                               source=ColumnDataSource({
                                   'x': [(layout[e[0]][0] + layout[e[1]][0]) / 2 for e in graph.edges()],
                                   'y': [(layout[e[0]][1] + layout[e[1]][1]) / 2 for e in graph.edges()],
                                   'text': [graph.edges[e][NetContainer._DELAY_TIME_KEY] for e in graph.edges()]}))
    labels_for_edge.text_font_size = '10pt'
    labels_for_edge.background_fill_color = 'white'

    # Refresh the labels.
    fig.center.clear()
    fig.add_layout(labels_for_node, 'center')
    fig.add_layout(labels_for_edge, 'center')
