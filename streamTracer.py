import numpy as np

from bokeh.driving import count
from bokeh.layouts import column, gridplot, row
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.plotting import curdoc, figure
from bokeh.server.server import Server
from bokeh.palettes import Category20,Category20_20
from bokeh.models import LinearAxis, Range1d

from parameters import *
from mqttClient import new_data, reset_new_data, startMqttClient
# client = startMqttClient()

def bokehApp(doc):

    source = ColumnDataSource(getEmptyData())

    fPerf = figure(plot_height=100, tools="xpan,xwheel_zoom,xbox_zoom,reset")
    fPerf.line(x='time', y='dt', source=source)
    fPerf.x_range.follow = "end"
    fPerf.x_range.follow_interval = 100
    fPerf.x_range.range_padding = 0


    colors = Category20[20].__iter__()
    fCurrent = figure(plot_height=300, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_range=fPerf.x_range)
    fCurrent.line(x='time', y='wheelCurrent', source=source,legend=' wheelCurrent', color = next(colors))
    fCurrent.line(x='time', y='bladeCurrent', source=source,legend=' bladeCurrent', color = next(colors))
    # Setting the second y axis range name and range
    fCurrent.extra_y_ranges = {"tension": Range1d(start=10, end=15)}
    # Adding the second axis to the plot.  
    fCurrent.add_layout(LinearAxis(y_range_name="tension"), 'right')
    fCurrent.line(x='time', y='batteryVoltage', source=source, y_range_name="tension",legend=" %s"%'batteryVoltage', color = next(colors))
    fCurrent.legend.location = "top_left"
    fCurrent.legend.click_policy="hide"



    speedPlot = [ 'speed filtered command', 'rotation filtered command',
            'leftMotor speed', 'leftMotor filtered Speed',
            'rightMotor speed', 'rightMotor filtered Speed',
            ]
    p = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_range=fPerf.x_range)

    # print(Category20)
    # raise()

    for varName, color in zip(speedPlot,Category20[20]):
        print(color)
        p.line(x='time', y=varName, line_width=3, source=source, legend=' %s'%varName, color = color) #, alpha=0.2
        print(varName)

    p.legend.location = "top_left"
    p.legend.click_policy="hide"

    @count()
    def update(t):
        # print("nex_data",new_data)
        source.stream(new_data, 300)
        reset_new_data()

    doc.add_root(column( gridplot([[fPerf],[p],[fCurrent]], toolbar_location="left", plot_width=1000)))
    doc.add_periodic_callback(update, 100)
    doc.title = "streamTracer"

# bokehApp(curdoc())
def startBokehApp():
    server = Server({'/': bokehApp}, num_procs=1)
    server.start()

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()







# import panel as pn
# from bokeh.layouts import column, row

# def plotpanel():
#     source = ColumnDataSource(getEmptyData())

#     fPerf = figure(plot_height=100, tools="xpan,xwheel_zoom,xbox_zoom,reset")
#     fPerf.line(x='time', y='dt', source=source)
#     fPerf.x_range.follow = "end"
#     fPerf.x_range.follow_interval = 100
#     fPerf.x_range.range_padding = 0

#     p = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_range=fPerf.x_range)

#     # print(Category20)
#     # raise()

#     for varName, color in zip(debugData[1:],Category20[20]):
#         print(color)
#         p.line(x='time', y=varName, line_width=3, source=source, legend=' %s'%varName, color = color) #, alpha=0.2
#         print(varName)

#     p.legend.location = "top_left"
#     p.legend.click_policy="hide"

#     @count()
#     def update(t):
#         print(new_data)
#         source.stream(new_data, 300)
#         reset_new_data()

#     # doc.add_root(column( gridplot([[fPerf],[p]], toolbar_location="left", plot_width=1000)))
#     # doc.add_periodic_callback(update, 100)
#     # doc.title = "streamTracer"
#     # return doc

#     bokeh_pane = pn.pane.Bokeh(column(fPerf,p))
#     bokeh_pane.servable()
#     # pn.state.add_periodic_callback(update, 100)
#     bokeh_pane.add_periodic_callback(update, 100)
#     bokeh_pane.show()

