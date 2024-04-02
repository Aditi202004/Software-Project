# Required imports for connecting the devices with PC
import pyvisa, telnetlib

# Required imports for plotting the graph
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
import types

# Required import for interface
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from threading import Thread
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Required imports for maintaining the data
import csv, json
import numpy as np

# Required import to make the program sleep
import time

# Required import for Directories of files
from datetime import datetime
import os
from os.path import exists
from os import mkdir

# Array to store the lines...
ARRAY_OF_PLOTTING_LINES = {
    "ResVsTemp":[[100],[100]],
    "223":[[1],[2]],
    "234":[[1],[3]], 
    "245":[[3],[4]]
}
ARRAY_OF_SELECTED_TEMPERATUES = ["223", "234", "245"]
selected_temperature = None  # Initialize selected_temperature globally
# Function to updates the content in the annotation...
def UPDATE_ANNOTATION(ind, ARRAY_OF_PLOTTING_LINES, annotations):
    x, y = ARRAY_OF_PLOTTING_LINES.get_data()
    annotations.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
    annotations.set_text("Temperature : {}, Resistance: {}".format(x[ind["ind"][0]], y[ind["ind"][0]]))
    annotations.get_bbox_patch().set_alpha(0.4)

# Function used to display the annotation when hover...
def DISPLAY_ANNOTATION_WHEN_HOVER(event, ARRAY_OF_PLOTTING_LINES, annotations):
    try:
        vis = annotations.get_visible()
        if event.inaxes:
            for line in ARRAY_OF_PLOTTING_LINES.values():
                cont, ind = line.contains(event)
                if cont:
                    UPDATE_ANNOTATION(ind, line, annotations)
                    annotations.set_visible(True)
                    event.canvas.draw_idle()
                    return
            if vis:
                annotations.set_visible(False)
                event.canvas.draw_idle()
    except:
        pass

# Function used to zoom out and in graph using mouse...
def ZOOM_INOUT_USING_MOUSE(event):
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

# Function which enables the functionality of all keys(Ctrl, Shift,etc..) ...
def KEY_PRESS_HANDLER(event, canvas, toolbar):
    key_press_handler(event, canvas, toolbar)

# Function to add the new point to the graph...
def ADD_POINT_TO_GRAPH(NEW_X_COORDINATES, NEW_Y_COORDINATES, temp=None):
    global CANVAS_OF_GRAPH

    if temp:
        ARRAY_OF_PLOTTING_LINES[str(temp)][0].append(NEW_X_COORDINATES)
        ARRAY_OF_PLOTTING_LINES[str(temp)][1].append(NEW_Y_COORDINATES)
    else:
        ARRAY_OF_PLOTTING_LINES["Res_Vs_Temp"][0].append(NEW_X_COORDINATES)
        ARRAY_OF_PLOTTING_LINES["Res_Vs_Temp"][1].append(NEW_Y_COORDINATES)

    x_data = ARRAY_OF_PLOTTING_LINES[str(temp)][0] if temp else ARRAY_OF_PLOTTING_LINES["Res_Vs_Temp"][0]
    y_data = ARRAY_OF_PLOTTING_LINES[str(temp)][1] if temp else ARRAY_OF_PLOTTING_LINES["Res_Vs_Temp"][1]

    PLOTTING_LINE.set_data(np.array(x_data), np.array(y_data))
    # update the view limits as per the newly added points
    GRAPH.relim()
    GRAPH.autoscale_view()
    CANVAS_OF_GRAPH.draw_idle()



# Function to save the graph plot image to selected directory...
def SAVE_THE_GRAPH_INTO(directory):
    global selected_temperature
    IMAGE_FILE_NAME = "Plot at "+selected_temperature+ " K "+ TITLE + ".png"
    GRAPH_IMAGE_PATH = os.path.join(directory, IMAGE_FILE_NAME)
    CANVAS_OF_GRAPH.figure.savefig(GRAPH_IMAGE_PATH)

def UPDATE_GRAPH(*args):
    global selected_temperature
    selected_temperature = str(temperature_combobox.get())

    if selected_temperature == "ResVsTemp":
        LABEL_OF_GRAPH.config(text="Resistance Vs. Temperature")
        PLOTTING_LINE.set_data(np.array(ARRAY_OF_PLOTTING_LINES["ResVsTemp"][0]),np.array(ARRAY_OF_PLOTTING_LINES["ResVsTemp"][1]))
        GRAPH.set_xlabel("TEMPERATURE") # Set X label
        GRAPH.set_ylabel("RESISTANCE") # Set Y label


    else:
        LABEL_OF_GRAPH.config(text="Resistance Vs Time at "+selected_temperature+" K")
        PLOTTING_LINE.set_data(np.array(ARRAY_OF_PLOTTING_LINES[selected_temperature][0]),np.array(ARRAY_OF_PLOTTING_LINES[selected_temperature][1]))
        GRAPH.set_xlabel("TIME") # Set X label
        GRAPH.set_ylabel("RESISTANCE") # Set Y label

    GRAPH.relim()
    GRAPH.autoscale_view()
    CANVAS_OF_GRAPH.draw_idle()

# Function to setup the Graph in Graph tab...
def SET_GRAPH_IN_TAB(GRAPH_TAB):
    global FRAME_OF_GRAPH, LABEL_OF_GRAPH, FIGURE_OF_GRAPH, CANVAS_OF_GRAPH, GRAPH, ANNOTATION, TOOLBAR_OF_GRAPH, temperature_combobox, selected_temperature, PLOTTING_LINE

    FRAME_OF_GRAPH = Frame(GRAPH_TAB) 

    LABEL_OF_GRAPH = tk.Label(FRAME_OF_GRAPH, text = "Resistance Vs. Temperature") # Adding label/title for the graph
    LABEL_OF_GRAPH.config(font=('Times', 32)) # Changing the default font style and size to Times and 32
    temperature_combobox = tb.Combobox(FRAME_OF_GRAPH, font=("Arial", 10), state='readonly')
    temperature_combobox['values'] = list(temperature_combobox['values']) + ["ResVsTemp"] + ARRAY_OF_SELECTED_TEMPERATUES
    temperature_combobox.set("ResVsTemp")


    temperature_combobox.bind("<<ComboboxSelected>>", UPDATE_GRAPH)

    FIGURE_OF_GRAPH = Figure(figsize=(6, 4.5)) # Created a figure to add graph

    CANVAS_OF_GRAPH = FigureCanvasTkAgg(FIGURE_OF_GRAPH, master = FRAME_OF_GRAPH) # Created a canvas to plot graph

    GRAPH = FIGURE_OF_GRAPH.add_subplot(111)  # Add a subplot with index (e.g., 111) for a single subplot

    GRAPH.set_xlabel("TEMPERATURE") # Set X label
    GRAPH.set_ylabel("RESISTANCE") # Set Y label
    GRAPH.grid() # Added grids to graph
    GRAPH.axhline(linewidth=2, color='black') # Added X axis
    GRAPH.axvline(linewidth=2, color='black') # Added Y axis

    ANNOTATION = GRAPH.annotate("", xy=(0,0), xytext = (-150,25),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->")) # Annotion means when we hover cursor to a point a small box will appear displaying the x and y co-ordinates

    ANNOTATION.set_visible(False) # Making it invisible initially (We will make it visible when we hover the cursor in DISPLAY_ANNOTATION_WHEN_HOVER Function)

    TOOLBAR_OF_GRAPH = NavigationToolbar2Tk(CANVAS_OF_GRAPH, FRAME_OF_GRAPH) # Added toolbar for graph
    TOOLBAR_OF_GRAPH.pan() # Made the graph is in pan mode... Simply pan mode is selected... Pan mode means the mode where you can move the graph... (+ kind of symbol in the toolbar)...

    PLOTTING_LINE, = GRAPH.plot([], [], color="orange", linestyle="-", marker="o", markerfacecolor="blue", markeredgewidth=1, markeredgecolor="black" ) # Plotted an empty graph...


    # Making zooming, hovering by mouse
    CANVAS_OF_GRAPH.mpl_connect("key_press_event", lambda event: KEY_PRESS_HANDLER(event, CANVAS_OF_GRAPH, TOOLBAR_OF_GRAPH))
    CANVAS_OF_GRAPH.mpl_connect('scroll_event', ZOOM_INOUT_USING_MOUSE)
    CANVAS_OF_GRAPH.mpl_connect("motion_notify_event", lambda event: DISPLAY_ANNOTATION_WHEN_HOVER(event, ARRAY_OF_PLOTTING_LINES, ANNOTATION))

    # Making Canvas, Label, Frame visible in the tab by packing
    temperature_combobox.pack(padx=10, pady=(30,20))
    LABEL_OF_GRAPH.pack(pady=(0,0))
    CANVAS_OF_GRAPH.get_tk_widget().pack()
    FRAME_OF_GRAPH.pack(fill="both", expand=True)

TITLE = "helloo"

INTERFACE = tb.Window(themename="yeti") # Made a root Interface
# GRAPH_TAB = tb.Frame(INTERFACE)

SET_GRAPH_IN_TAB(INTERFACE)
ADD_POINT_TO_GRAPH(1,1,223)
ADD_POINT_TO_GRAPH(2,2,223)
INTERFACE.mainloop()
