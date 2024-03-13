from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler, NavigationToolbar2
from matplotlib.figure import Figure


import types
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import numpy as np


class Grapher: # this class controls the graph & it's ploting
    def __init__(self,r):
        self.line = None

        self.plot_data={"Temp" : [],
                        "Resistance" : []}

        # self.x_plot = "Temp"
        # self.y_plot = "Resistance"

        self.frame=Frame(r)
        self.fig = Figure(figsize=(8, 5), dpi=100)
        # self.triggered=False
        
        self.ax=self.fig.add_subplot(3,3,1)
        # self._clear()
        self.ax.set_xlabel("Temp")
        self.ax.set_ylabel("Resistance")
        
        self.ax.cla() # for clearing entire thing....we have to add grids and all after this
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)  # A tk.DrawingArea.
        self.ax.plot(np.array([1,2]), np.array([1,2]), "-o")

        self.ax.grid()
        self.ax.axhline(linewidth=2, color='black')
        self.ax.axvline(linewidth=2, color='black')
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        self.canvas.draw_idle()
        self.canvas.set_cursor=lambda x:None # to avoid flickering
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame) # toolbar

        self.toolbar.pan()

        self.toolbar.set_cursor=lambda x:None # to avoid flickering
        self.canvas.get_tk_widget().pack(side=TOP, expand=1,fill="both") # DO NOT COMMENT THIS - this line is for displaying the canvas
        # self.toolbar.update()

        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.canvas.mpl_connect('scroll_event',self.mousewheel_move)

        self.canvas.mpl_connect("motion_notify_event", self.hover)

    def plot_point(self, temp, res):
        #clearing the canvas and adding a grid
        self.ax.cla()
        self.ax.grid()
        self.ax.axhline(linewidth=2, color='black')
        self.ax.axvline(linewidth=2, color='black')

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        try:
            self.line, = self.ax.plot(np.array(self.plot_data["Temp"]), np.array(self.plot_data["Resistance"]), "-o")
            self.canvas.draw_idle()
        except Exception as e:
            print("cannot _plot, x_plot=",self.x_plot," y_plot=",self.y_plot,"error=",e)
            pass


    def update_annot(self,ind): #updates the popup indicating x & y values
        x,y = self.line.get_data()
        self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        self.annot.set_text("Temperature : {}  Resistance : {}".format(x[ind["ind"][0]], y[ind["ind"][0]]))
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self,event): #signals to show popup when hovering over any point
        if(self.line==None):
            return

        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.line.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()