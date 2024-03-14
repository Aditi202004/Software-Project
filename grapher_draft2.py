import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
import tkinter as tk
import numpy as np
import types

root = tk.Tk()
last_x = 3
last_y = 7

def update_annot(ind, line, annotations):
    x, y = line.get_data()
    annotations.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
    annotations.set_text("x: {}\ny: {}".format(x[ind["ind"][0]], y[ind["ind"][0]]))
    annotations.get_bbox_patch().set_alpha(0.4)

def hover(event, line, annotations):
    vis = annotations.get_visible()
    if event.inaxes:
        cont, ind = line.contains(event)
        if cont:
            update_annot(ind, line, annotations)
            annotations.set_visible(True)
            event.canvas.draw_idle()
        else:
            if vis:
                annotations.set_visible(False)
                event.canvas.draw_idle()

def mousewheel_move(event):
    graph = event.inaxes
    try:
        graph._pan_start = types.SimpleNamespace(
            lim=graph.viewLim.frozen(),
            trans=graph.transData.frozen(),
            trans_inverse=graph.transData.inverted().frozen(),
            bbox=graph.bbox.frozen(),
            x=event.x,
            y=event.y)
        if event.button == 'up':
            graph.drag_pan(3, event.key, event.x + 10, event.y + 10)
        else:
            graph.drag_pan(3, event.key, event.x - 10, event.y - 10)
        fig = graph.get_figure()
        fig.canvas.draw_idle()
    except:
        pass
    

def on_key_press(event, canvas, toolbar):
    key_press_handler(event, canvas, toolbar)

def add_point_to_graph(new_x, new_y, line, canvas):
    global last_x, last_y
    x_ = float(new_x.get())
    y_ = float(new_y.get())
    line.set_data(np.append(line.get_xdata(), x_), np.append(line.get_ydata(), y_))
    canvas.draw_idle()
    last_x = x_
    last_y = y_





frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

label_for_graph = tk.Label(frame, text="Resistance Vs. Temperature")
label_for_graph.config(font=('Times', 32))
label_for_graph.pack()

figure_of_graph = Figure()
canvas_for_graph = FigureCanvasTkAgg(figure_of_graph, master=frame)
canvas_for_graph.get_tk_widget().pack(fill="both", expand=True)
graph = figure_of_graph.add_subplot(111)  # Add a subplot with index (e.g., 111) for a single subplot


graph.set_xlabel("TEMPERATURE")
graph.set_ylabel("RESISTANCE")
graph.grid() 
graph.axhline(linewidth=2, color='black')
graph.axvline(linewidth=2, color='black')
x = np.array([1,2,3])
y = np.array([5,2,7])
annotations = graph.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
annotations.set_visible(False)

line, = graph.plot(x, y, color="orange", linestyle="-", marker="o", markerfacecolor="blue", markeredgewidth=1, markeredgecolor="black")

canvas_for_graph.mpl_connect("key_press_event", lambda event: on_key_press(event, canvas_for_graph, toolbar_for_graph))
canvas_for_graph.mpl_connect('scroll_event', mousewheel_move)
canvas_for_graph.mpl_connect("motion_notify_event", lambda event: hover(event, line, annotations))

toolbar_for_graph = NavigationToolbar2Tk(canvas_for_graph, frame)
toolbar_for_graph.update()
toolbar_for_graph.pack()
toolbar_for_graph.pan()

root.mainloop()
