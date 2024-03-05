

from tkinter import *
from tkinter import ttk
from tkinter import messagebox,filedialog
# import json, pyvisa, types, math, os, time, threading, functools
# import numpy as np
import types
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler, NavigationToolbar2
from matplotlib.figure import Figure

from datetime import datetime
from os.path import exists
from os import mkdir

# from telnetlib import Telnet
tab_bg="#575757"
selected_bg="#8a8a8a"
def confirm(): #confirmation before quiting Gui
   if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # if(impedance_device_valid):
        #     export_config()
        root.destroy()
        
def toggle_ser_par(): # clicking on button toggles between series and parallel
    ser_par_btn["text"] = "Parallel" if ser_par_btn["text"]=="Series" else "Series"

def toggle_bias(): # toggles bias button on & off
    bias_stat_btn["text"] = "-" if bias_stat_btn["text"]=="+" else "+"

def set_entry(entry_widget,text): # sets the value of any entry/textbox with the given text
    entry_widget.delete(0,'end')
    entry_widget.insert(0,str(text).strip())
    
def check_freq(val,freq_type): #checks if given frequency is within range
    try:
        val=val.strip()
        f_val=float(val)
        if(f_val<20 or f_val>120e6):
            messagebox.showinfo("Alert","Out of Range: "+freq_type+" !\nMin: 20 Max: 120e+6")
            return -1
    except:
        messagebox.showinfo("Alert","Invalid Input for: "+freq_type+" !")
        return -1
    
    return 1

def center_geo(window_width,window_height): # returns center values for any widget according to pc screen

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))-25

    return "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)
### graph functions ###
NavigationToolbar2.toolitems = ( # to hide pan an zoom options (auto enabled by default)
('Home', 'Reset original view', 'home', 'home'),
('Back', 'Back to  previous view', 'back', 'back'),
('Forward', 'Forward to next view', 'forward', 'forward'),
(None, None, None, None),
(None, None, None, None),
('Subplots','Configure subplots','subplots','configure_subplots'), # (None, None, None, None),
('Save', 'Save the figure', 'filesave', 'save_figure'))

class Grapher: # this class controls the graph & it's ploting
    def __init__(self,r):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
        self.line = None

        self.plot_data={}

        self.x_plot=None
        self.y_plot=None
        
        self.frame=Frame(r)
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.triggered=False
        
        self.ax=self.fig.add_subplot(1,1,1)
        self._clear()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)  # A tk.DrawingArea.
        self.canvas.draw_idle()
        self.canvas.set_cursor=lambda x:None # to avoid flickering
        self.canvas.get_tk_widget().pack(side=TOP, expand=1,fill="both")

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame) # toolbar

        self.toolbar.pan()

        self.toolbar.set_cursor=lambda x:None # to avoid flickering
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, expand=1)

        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.canvas.mpl_connect('scroll_event',self.mousewheel_move)

        self.canvas.mpl_connect("motion_notify_event", self.hover)

    def is_triggered(self,val): # checks if triggered, if so disables pan else enables pan
        self.triggered=val
        try:
            self.toolbar.pan()
        except: pass

    def _set_plot(self,prop1,prop2): # sets what properties are to be plotted & assigns x y label accordingly
        self._clear()
        self.ax.set_xlabel(term_names[prop1])
        self.ax.set_ylabel(term_names[prop2])

        self.x_plot=prop1
        self.y_plot=prop2

        self.canvas.draw_idle()

    def _plot(self,impedance_only=True): # plots whatever changes are made to the graph data
        try:
            if(impedance_only):
                    len_x=len(self.plot_data[self.x_plot])
                    len_y=len(self.plot_data[self.y_plot])
                    if( len_x< len_y):
                        temp_y=self.plot_data[self.y_plot][:len_x-1]
                        self.line, =self.ax.plot(self.plot_data[self.x_plot],temp_y,"-o")
                    elif( len_x> len_y):
                        temp_x=self.plot_data[self.x_plot][:len_y-1]
                        self.line, =self.ax.plot(temp_x,self.plot_data[self.y_plot],"-o")
                    else:
                        self.line, =self.ax.plot(self.plot_data[self.x_plot],self.plot_data[self.y_plot],"-o")

                    self.canvas.draw_idle()
            else:
                len_x=len(self.plot_data[self.x_plot])
                len_y=len(self.plot_data[self.y_plot][plot_freq])
                if( len_x< len_y):
                    print("line 1")
                    self.line, =self.ax.plot(np.array(self.plot_data[self.x_plot]),np.array(self.plot_data[self.y_plot][plot_freq][:len_x-1]),"-o")
                elif( len_x> len_y):
                    print("line 2")
                    self.line, =self.ax.plot(np.array(self.plot_data[self.x_plot][:len_y-1]),np.array(self.plot_data[self.y_plot][plot_freq]),"-o")
                else:
                    print("line 3")
                    self.line, =self.ax.plot(self.plot_data[self.x_plot],self.plot_data[self.y_plot][plot_freq],"-o")

                self.canvas.draw_idle()
        except Exception as e:
            print("cannot _plot, x_plot=",self.x_plot," y_plot=",self.y_plot,"error=",e)
            pass

    def _clear(self): # clears all previous plotted data
        self.ax.cla()
        self.ax.grid()
        self.ax.axhline(linewidth=2, color='black')
        self.ax.axvline(linewidth=2, color='black')

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        

    def update_annot(self,ind): #updates the popup indicating x & y values
        x,y = self.line.get_data()
        self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        self.annot.set_text("x: {}\ny: {}".format(x[ind["ind"][0]], y[ind["ind"][0]]))
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


    def mousewheel_move(self,event): #to allow scrolling for zooming in & out
        if(self.triggered):
            return

        self.ax=event.inaxes
        self.ax._pan_start = types.SimpleNamespace(
                lim=self.ax.viewLim.frozen(),
                trans=self.ax.transData.frozen(),
                trans_inverse=self.ax.transData.inverted().frozen(),
                bbox=self.ax.bbox.frozen(),
                x=event.x,
                y=event.y)
        if event.button == 'up':
            self.ax.drag_pan(3, event.key, event.x+10, event.y+10)
        else:
            self.ax.drag_pan(3, event.key, event.x-10, event.y-10)
        self.fig=self.ax.get_figure()
        self.fig.canvas.draw_idle()

    def on_key_press(self,event): #propogates every click even to their respective button in matplotlib
        key_press_handler(event, self.canvas, self.toolbar)

def set_plot_prop(event): # changes what property is currently being ploted when selected from the dropdown box
    if(impedance_only_var.get()):
        graph._set_plot("Freq",plot_property_var.get())
        graph._plot()
    else:
        graph._set_plot("Temp",plot_property_var.get())
        graph._plot(False)

if __name__=="__main__":
    ### window setting ###
    root = Tk()
    root.wm_title("TD-Controller")
    root.grid_columnconfigure(0,weight=1)
    root.grid_rowconfigure(0,weight=1)

    impedance_only_var=IntVar()

    ### positioning widgets ###

    ## sidebar ##
    side_bar_frame=Frame(root,bg="#878787")
    side_bar_frame.grid(row=0,column=1,rowspan=2, sticky="nswe")

    settings_btn= Button(side_bar_frame,text="Settings",height= 2)
    settings_btn.pack(side="bottom",pady=(5,2),fill='x',padx=2)

    info_btn= Button(side_bar_frame,text="Info",height= 2)
    info_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    sync_set_btn= Button(side_bar_frame,text="Sync Set",height= 2)
    sync_set_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    sync_get_btn= Button(side_bar_frame,text="Sync Get",height= 2)
    sync_get_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    trigger_btn= Button(side_bar_frame,text="Trigger",height=2)
    trigger_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    ## notebook tabs ##
    ControlPanel = ttk.Notebook(root)

    ctc_tab = Frame(ControlPanel,bg=tab_bg) #CTC config tab
    wayne_tab = Frame(ControlPanel,bg=tab_bg) #wayne config tab
    graph_tab = Frame(ControlPanel) #graphing config tab

    ControlPanel.add(ctc_tab, text =' CTC\n Setup ')
    ControlPanel.add(wayne_tab, text =' Current Source\n      Setup ')
    ControlPanel.add(graph_tab, text =' Graph\n Setup ')
    ControlPanel.grid(row=0,column=0,sticky="nswe")

    # for i in ControlPanel.tabs():
    #     ControlPanel.tab(i, state="disabled")
    
    ### graph options ###
    graph_options=Frame(graph_tab)
    graph_options.pack(fill="x",expand=True,pady=(10,0))
    graph_options.grid_columnconfigure(0, weight=1)
    graph_options.grid_columnconfigure(1, weight=1)
    graph_options.grid_columnconfigure(2, weight=1)


    # plot_property_var=StringVar(value="< Awaiting Trigger >")
    # plot_property = ttk.Combobox(graph_options,textvariable =plot_property_var,state="readonly")
    # plot_property.grid(row=1,column=0)
    # plot_property.bind('<<ComboboxSelected>>',set_plot_prop)

    # Label(graph_options,text="Plot Frequency(Hz)").grid(row=0,column=1,sticky="s")
    # plot_freq_entry= Entry(graph_options)
    # plot_freq_entry.grid(row=1,column=1,sticky="s")

    # update_freq_btn= Button(graph_options,width=13,text="Update Frequency")
    # update_freq_btn.grid(row=1,column=2,sticky="s",ipadx=5)

    ## Graph ##  
    graph=Grapher(graph_tab)
    graph.frame.pack(side=TOP,fill="both",expand=True,pady=(10,0))
    


    # title #
    title_lframe=LabelFrame(wayne_tab,text="Title",fg="white",bg=tab_bg)
    title_lframe.grid(row=0,column=0,columnspan=4,sticky="new",pady=20,padx=200)

    title_entry=Entry(title_lframe,font=(10),width=20)
    title_entry.pack(pady=(0,5),padx=10,ipady=5)
    

    ### Drive ###
    drive_lframe= LabelFrame(wayne_tab,text="Drive",fg="white",bg=tab_bg)
    drive_lframe.grid(row=1, column=0,rowspan=3, sticky="nswe",padx=200,pady=25)

    
    # # add to manual: For Level Add 'A' / 'V' at end for Amps / Volts respectively

    freq_start_lframe=LabelFrame(drive_lframe,text="Current Start Value (A)",fg="white",bg=tab_bg)
    freq_start_lframe.grid(row=0,column=0,padx=10,pady=(5,10),sticky="w")

    freq_start_entry=Entry(freq_start_lframe,font=(10),width=20)
    freq_start_entry.grid(row=0,column=0,rowspan=2,pady=10,padx=10,ipady=5)


    freq_stop_lframe=LabelFrame(drive_lframe,text="Current Stop (A)",fg="white",bg=tab_bg)
    freq_stop_lframe.grid(row=1,column=0,padx=10,pady=(5,10),sticky="w")

    freq_stop_entry=Entry(freq_stop_lframe,font=(10),width=20)
    freq_stop_entry.grid(row=0,column=0,rowspan=3,pady=10,padx=10,ipady=5)


    freq_interval_lframe=LabelFrame(drive_lframe,text="Interval",fg="white",bg=tab_bg)
    freq_interval_lframe.grid(row=2,column=0,padx=10,pady=(5,10),sticky="w")

    freq_interval_entry=Entry(freq_interval_lframe,font=(10),width=20)
    freq_interval_entry.grid(row=0,column=0,rowspan=3,pady=10,padx=10,ipady=5)
    
    # freq_log_var=IntVar()
    # Checkbutton(freq_interval_lframe,text="Log",fg="white",bg=tab_bg,highlightthickness=0,variable=freq_log_var, activebackground=tab_bg, activeforeground='white',selectcolor="black").grid(row=0,column=1,sticky="s",padx=(0,5))


    # level_lframe=LabelFrame(drive_lframe,text="Level (A/V)",fg="white",bg=tab_bg)
    # level_lframe.grid(row=4,column=0,columnspan=2,padx=10,pady=(5,10),sticky="w")

    # level_entry=Entry(level_lframe,font=(10),width=20)
    # level_entry.grid(row=0,column=0,rowspan=2,pady=10,padx=10,ipady=5)

    
    # bias_lframe=LabelFrame(drive_lframe,text="Current Start(A)",fg="white",bg=tab_bg)
    # bias_lframe.grid(row=0,column=0,columnspan=2,padx=10,pady=(5,10))

    # bias_entry=Entry(bias_lframe,font=(10),width=20)
    # bias_entry.grid(row=0,column=0,rowspan=2,pady=10,padx=10,ipady=5)

    # bias_stat_btn=Button(bias_lframe,text="+",height= 2,width=10,command=toggle_bias) #Bias ON/OFF
    # bias_stat_btn.grid(row=0,column=1,rowspan=2,pady=10,padx=10,ipady=5)

        ### other ###
    root.protocol("WM_DELETE_WINDOW", confirm)
    root.wait_visibility()
    root.update()
    
    root_width=root.winfo_width()
    root_height=root.winfo_height()
    root.geometry(center_geo(root_width,root_height))
    root.minsize(root_width,root_height)

    # get_settings()

    # impedance_only_var.set(settings["impedance_only"])
    # toggle_impedance_only()

    # connect_device()
    # initial_setup()

    root.mainloop()
