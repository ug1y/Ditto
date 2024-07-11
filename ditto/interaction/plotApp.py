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
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.document import Document
from bokeh.io import curdoc
from bokeh.plotting import figure


class PlotApp(Application):
    def __init__(self):
        self.counter = 1
        handler = FunctionHandler(self.modify_doc)
        super().__init__(handler)

    def modify_doc(self, doc: Document):
        plot = figure(name="bokeh_figure")
        doc.add_root(plot)
        doc.add_periodic_callback(self.callback, 1000)

    def callback(self):
        self.counter += 1
        print("callback ", self.counter)


def CreatePlotApp():
    # Create a single PlotApp for each web request.
    return Application(FunctionHandler(lambda doc: PlotApp().modify_doc(doc)))


# Use for running command: `bokeh serve --show ditto\interaction\plotApp.py`
PlotApp().modify_doc(curdoc())
