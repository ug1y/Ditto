# myapp.py

from bokeh.document import Document
from bokeh.io import curdoc
from bokeh.plotting import figure

i = 0


def callback():
    global i
    i += 1
    print("callback ", i)


def myapp(doc: Document):
    doc.title = "Ditto: A BlockDAG Simulation Framework"
    plot = figure(name="bokeh_figure")
    doc.add_root(plot)
    doc.add_periodic_callback(callback, 1000)


myapp(curdoc())
