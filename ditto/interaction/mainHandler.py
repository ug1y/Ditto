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
import webbrowser
from os.path import join, dirname

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import CDN
from jinja2 import Environment, FileSystemLoader
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, StaticFileHandler


class MainHandler(RequestHandler):
    def initialize(self) -> None:
        # This method is invoked before every request.
        pass

    def get(self):
        # Load template using jinja2.
        env = Environment(loader=FileSystemLoader(join(dirname(__file__), 'templates')))
        template = env.get_template('index.html')

        title = "A BlockDAG Simulation Framework"
        # Get bokeh resources.
        resources = CDN.render()

        # Plot a figure using bokeh.
        plot = figure(title="Simple line example", x_axis_label='x', y_axis_label='y',
                      sizing_mode='stretch_width')
        plot.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])
        script, div = components(plot)

        # Write properties to render template.
        self.write(template.render(title=title, resources=resources, script=script, div=div))

    def on_finish(self) -> None:
        print("finish")


def RunServer():
    # Start a Tornado server to render page.
    tornado_app = Application([
        (r"/", MainHandler),
        (r"/static/(.*)", StaticFileHandler, {"path": join(dirname(__file__), "static")})
    ])
    tornado_app.listen(7006)

    # Open default web browser to show site.
    IOLoop.current().add_callback(webbrowser.open, "http://localhost:7006/")
    IOLoop.current().start()
