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

from bokeh.embed import server_document
from bokeh.server.server import Server
from jinja2 import Environment, FileSystemLoader
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

from .plotApp import PlotApp, CreatePlotApp


class MainHandler(RequestHandler):
    def get(self):
        # Load template using jinja2.
        env = Environment(loader=FileSystemLoader(join(dirname(__file__), 'templates')))
        template = env.get_template('index.html')

        # Set properties for html template.
        title = "My Bokeh App"
        script = server_document('http://localhost:5006/myapp')

        # Write properties to html template.
        self.write(template.render(title=title, plot_script=script))


def RunServer():
    # Start a Bokeh server to plot blockdag.
    bokeh_server = Server({'/myapp': PlotApp()}, allow_websocket_origin=["localhost:5006", "localhost:7006"])
    bokeh_server.start()

    # Start a Tornado server to render page.
    tornado_app = Application([(r"/", MainHandler)])
    tornado_app.listen(7006)

    # Open default web browser to show site.
    IOLoop.current().add_callback(webbrowser.open, "http://localhost:7006/")
    IOLoop.current().start()
