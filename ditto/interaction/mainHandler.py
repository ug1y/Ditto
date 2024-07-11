import webbrowser
from os.path import join, dirname

from bokeh.embed import server_document
from bokeh.server.server import Server
from jinja2 import Environment, FileSystemLoader
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

from .myapp import myapp


class MainHandler(RequestHandler):
    def get(self):
        env = Environment(loader=FileSystemLoader(join(dirname(__file__), 'templates')))
        template = env.get_template('index.html')

        title = "My Bokeh App"
        script = server_document('http://localhost:5006/myapp')

        self.write(template.render(title=title, plot_script=script))


def RunServer():
    bokeh_server = Server({'/myapp': myapp}, allow_websocket_origin=["localhost:5006", "localhost:7006"])
    bokeh_server.start()

    tornado_app = Application([(r"/", MainHandler)])
    tornado_app.listen(7006)
    IOLoop.current().add_callback(webbrowser.open, "http://localhost:7006/")
    IOLoop.current().start()
