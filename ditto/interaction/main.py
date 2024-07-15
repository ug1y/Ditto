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
from bokeh.models import Button
from bokeh.plotting import figure, curdoc


def modify_doc(doc: Document):
    title = "Ditto: A Hybrid BlockDAG Simulation Framework"
    version = '0.1.0'
    doc.title = title
    # doc.template_variables['title'] = title
    doc.template_variables['version'] = version

    dag_plot = figure(name="figure", title="blockdag graph", sizing_mode='stretch_both')
    dag_plot.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])

    button = Button(name="button", label="click me", button_type="success")
    button.on_event("button_click", lambda: print("click!"))

    doc.add_root(dag_plot)
    doc.add_root(button)


# Create a new plot and add it to the document.
modify_doc(curdoc())

# Use `bokeh serve --show ditto\interaction` to run the server.
