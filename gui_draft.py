from tkinter import *
from tkinter import ttk
from tkinter import messagebox,filedialog
# import json, pyvisa, types, math, os, time, threading, functools
# import numpy as np
import types,json
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler, NavigationToolbar2
from matplotlib.figure import Figure

from datetime import datetime
from os.path import exists
from os import mkdir
settings_file="setting_data.json"
settings={"device_name":"GPIB0::6::INSTR",
"output_dir":"./",
"ctc_address":"192.168.0.2",
"ctc_telnet":"23",
"rs232":"COM 1"}


# from telnetlib import Telnet
tab_bg="#575757"
selected_bg="#8a8a8a"
def confirm(): #confirmation before quiting Gui
   if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # if(impedance_device_valid):
        #     export_config()
        root.destroy()
        
def write_settings(): #saves all changes made in the settings to the settings.json file
    global settings

    file_handler=open(settings_file, 'w',encoding='utf-8')
    file_handler.write(json.dumps(settings))

def center_geo(window_width,window_height): # returns center values for any widget according to pc screen

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))-25

    return "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)

def connect_device(): # connects to the devices & checks if are working

    loading_popup=Toplevel(root)
    loading_popup.config(bg="black")
    # loading_popup.attributes('-topmost', True)
    loading_popup.geometry(center_geo(200, 60))
    loading_popup.overrideredirect(True)
    loading_popup.resizable(False,False)

    Label(loading_popup,text="Checking Device...",fg="white",bg="black").place(relx=0.5,rely=0.5,anchor="center")

    loading_popup.grab_set()
    loading_popup.wait_visibility()
    root.update()

    # check_device(loading_popup)
    loading_popup.mainloop()

def set_settings(key,val): # changes them settings value then invokes function to write those changes to the file
    settings[key]=val
    write_settings()

def get_dir(out_dir_label): # sets the text on label after selecting output folder directory
    dirname = filedialog.askdirectory()
    if dirname:
        settings["output_dir"]=dirname
        write_settings()
        out_dir_label.config(text=dirname)
### popup window functions ###
def cancel_pop(popup,callback=None): # destroys popup & invokes given callback function afterwards
    popup.destroy()
    root.update()
    if(callback!=None):
        callback()
def show_settings_popup(): #shows settings popup
    global ctc_address_entry,ctc_telnet_entry, impedance_only_var

    write_settings()
    settings_popup=Toplevel(root)
    settings_popup.config(bg=tab_bg)
    settings_popup.title("Settings")
    settings_popup.geometry(center_geo(500, 270))
    settings_popup.resizable(False,False)

    settings_popup.grid_columnconfigure(0,weight=1)
    settings_popup.grid_columnconfigure(1,weight=1)

    Label(settings_popup,text="Nanovoltmeter",fg="white",bg=tab_bg).grid(row=0,column=0,rowspan=2,sticky="e",padx=(0,10),pady=10)
    
    option_inside = StringVar(value=settings["device_name"])

    device_options = ttk.Combobox(settings_popup, width = 27,textvariable = option_inside,state = "readonly")
    device_options.bind('<<ComboboxSelected>>',lambda x: set_settings("device_name",device_options.get()))
    device_options.grid(row=0,column=1,sticky="w",pady=10)

    # get_gpib_devices(device_options)

    Button(settings_popup,text="⟳").grid(row=0,column=1,padx=(120,0),pady=(10,5)) #command=lambda: get_gpib_devices(device_options)

    # Checkbutton(settings_popup,text="Impedance Only",fg="white",bg=tab_bg,highlightthickness=0,variable=impedance_only_var,command=toggle_impedance_only, activebackground=tab_bg, activeforeground='white',selectcolor="black").grid(sticky="w",row=1,column=1,pady=(0,10))

    ctc_address_var = StringVar(value=settings["ctc_address"])

    Label(settings_popup,text="CTC Address:",fg="white",bg=tab_bg).grid(row=2,column=0,sticky="e",padx=(0,10),pady=10)
    ctc_address_entry=Entry(settings_popup,font=(10),width=15,textvariable=ctc_address_var)
    ctc_address_entry.grid(row=2,column=1,pady=0,sticky="w")
    ctc_address_entry.bind("<KeyRelease>",lambda x: set_settings("ctc_address",ctc_address_var.get()))

    ctc_telnet_var = StringVar(value=settings["ctc_telnet"])

    Label(settings_popup,text="CTC Telnet:",fg="white",bg=tab_bg).grid(row=3,column=0,sticky="e",padx=(0,10),pady=10)
    ctc_telnet_entry=Entry(settings_popup,font=(10),width=15,textvariable=ctc_telnet_var)
    ctc_telnet_entry.grid(row=3,column=1,pady=0,sticky="w")
    ctc_telnet_entry.bind("<KeyRelease>",lambda x: set_settings("ctc_telnet",ctc_telnet_var.get()))
    
    rs232_var = StringVar(value=settings["rs232"])

    Label(settings_popup,text="RS232:",fg="white",bg=tab_bg).grid(row=4,column=0,sticky="e",padx=(0,10),pady=10)
    rs232_entry=Entry(settings_popup,font=(10),width=15,textvariable=rs232_var)
    rs232_entry.grid(row=4,column=1,pady=0,sticky="w")
    rs232_entry.bind("<KeyRelease>",lambda x: set_settings("rs232",rs232_var.get()))

    Label(settings_popup,text="Max_Retry:",fg="white",bg=tab_bg).grid(row=5,column=0,sticky="e",padx=(0,10),pady=10)
    max_retry_entry=Entry(settings_popup,font=(10),width=10)
    max_retry_entry.grid(row=5,column=1,pady=0,sticky="w")
  

    Label(settings_popup,text="Output Directory:",fg="white",bg=tab_bg).grid(row=6,column=0,sticky="e",padx=(0,10),pady=10)
    out_dir_label=Label(settings_popup,text=settings["output_dir"],anchor="w",width=25,fg="white",bg=tab_bg)
    out_dir_label.grid(row=6,column=1,sticky="w",padx=(0,10),pady=10)
    Button(settings_popup,text="Select Folder",command=lambda: get_dir(out_dir_label)).grid(row=6,column=1,padx=(150,0),pady=10)

    settings_popup.protocol("WM_DELETE_WINDOW") #lambda : cancel_pop(settings_popup,connect_device)
    settings_popup.grab_set()
    settings_popup.mainloop()
def show_info_popup(re_query=False): # shows popup containing both device names
    try:
        d_info="Nanovoltmeter Device: "+"BACKEND CODE TO CONNECT"+ "\nCurrent Source Device:" + "BACKEND CODE TO CONNECT"+ "\nCTC Device: "
        
        try:
            d_info+="BACKEND CODE TO CONNECT"
        except:
            d_info+="< Couldn't read, try again >"

        messagebox.showinfo("Device Info",d_info)
    except:
        # connect_device()
        if(not re_query):
            show_info_popup(True)
        else:
            messagebox.showinfo("Alert", "Invalid Query! Check code")
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

    # def is_triggered(self,val): # checks if triggered, if so disables pan else enables pan
    #     self.triggered=val
    #     try:
    #         self.toolbar.pan()
    #     except: pass

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
def configure_grid(event):
    # current_source_tab.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    # Calculate the new padding values based on window size
    padx = max(0, (width-200 ) // 2) 
    pady = max(0, (height - 500)//4 ) 
    # ctcpadx = max(0, (width-300 )//5 ) 
    # ctcpady = max(0, (height-500)//5 ) 



    title_lframe.grid_configure(padx=padx, pady=pady)
    drive_lframe.grid_configure(padx=padx, pady=pady)
    # io_frame.grid_configure(padx=padx, pady=pady)
    # limits_frame.grid_configure(padx=padx, pady=ctcpady)
    # temp_frame.grid_configure(padx=padx, pady=pady)
    # pid_lframe.grid_configure(padx=padx, pady=pady)

if __name__=="__main__":
    ### window setting ###
    root = Tk()
    root.wm_title("TD-Controller")
    root.geometry("850x600")
    root.grid_columnconfigure(0,weight=1)
    root.grid_rowconfigure(0,weight=1)


    ### positioning widgets ###

    ## sidebar ##
    side_bar_frame=Frame(root,bg="#878787")
    side_bar_frame.grid(row=0,column=1,rowspan=2, sticky="nswe")
    # side_bar_frame.grid_rowconfigure(0, weight=1)
    # side_bar_frame.grid_rowconfigure(1, weight=1)
    # side_bar_frame.grid_columnconfigure(0, weight=1)
    settings_btn= Button(side_bar_frame,text="Settings",height= 2,command=show_settings_popup)
    settings_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    info_btn= Button(side_bar_frame,text="Info",height= 2,command=show_info_popup)
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
    
    current_source_tab = Frame(ControlPanel,bg=tab_bg) #current source config tab
    graph_tab = Frame(ControlPanel) #graphing config tab

    ControlPanel.add(ctc_tab, text =' CTC\n Setup ')
    ControlPanel.add(current_source_tab , text =' Current Source\n      Setup ')
    ControlPanel.add(graph_tab, text =' Graph\n Setup ')
    ControlPanel.grid(row=0,column=0,sticky="nswe")

    ### graph options ###
    graph_options=Frame(graph_tab)
    graph_options.pack(fill="x",expand=True,pady=(10,0))
    graph_options.grid_columnconfigure(0, weight=1)
    graph_options.grid_columnconfigure(1, weight=1)
    graph_options.grid_columnconfigure(2, weight=1)


    ## Graph ##  
    graph=Grapher(graph_tab)
    graph.frame.pack(side=TOP,fill="both",expand=True,pady=(10,0))
    
    ## CTC tab ##
    # Configure grid weights for responsiveness
    # ctc_tab.grid_columnconfigure(0, weight=1)
    # ctc_tab.grid_rowconfigure(0, weight=1)
   
    # Input Selection
    io_frame = LabelFrame(ctc_tab, bg=tab_bg, borderwidth=0, highlightthickness=0)
    io_frame.grid(row=0, column=0, rowspan=3, pady=(20, 10), padx=120, sticky='nwes')
    # io_frame.grid_columnconfigure(0, weight=1)  # Make the first column growable
    # io_frame.grid_rowconfigure(0, weight=1)  # Make the first row growable
    # io_frame.grid_rowconfigure(1, weight=1)  # Make the first row growable
    # io_frame.grid_rowconfigure(2, weight=1)  # Make the first row growable
    
    
    input_label = Label(io_frame, text='Input:', bg=tab_bg, fg='white')
    input_label.grid(row=0, column=0,sticky="ew",padx=(20,20),pady=20)

    input_options = ['In 1', 'In 2', 'In 3']
    input_var = StringVar()
    input_dropdown = ttk.Combobox(io_frame, textvariable=input_var, values=input_options, state='readonly')
    input_dropdown.grid(row=0,column=1,rowspan=3,sticky="ew",pady=(10,10))
    input_dropdown.current(0)

    # Output Selection
    output_label = Label(io_frame, text='Output:', bg=tab_bg, fg='white')
    output_label.grid(row=0, column=2,sticky="ew",padx=(20,20),pady=20)

    output_options = ['Out 1', 'Out 2', 'Out 3']
    output_var = StringVar()
    output_dropdown = ttk.Combobox(io_frame, textvariable=output_var, values=output_options, state='readonly')
    output_dropdown.grid(row=0, column=3,rowspan=3,sticky="ew",pady=(10,10))
    
    output_dropdown.current(0)

    # Create the LabelFrame for limits and increments
    
    limits_frame = LabelFrame(ctc_tab, text='Power Controls', fg='white', bg=tab_bg)
    limits_frame.grid(row=3, column=0, rowspan=2, pady=(20, 10), padx=120, sticky='nwes')
    # limits_frame.grid_columnconfigure(0, weight=1)  # Make the first column growable
    # limits_frame.grid_rowconfigure(3, weight=1)  # Make the first row growable
    # limits_frame.grid_rowconfigure(4, weight=1)  # Make the first row growable
    
    # Low Limit
    low_limit_label = Label(limits_frame, text='Low Limit:', bg=tab_bg, fg='white')
    low_limit_label.grid(row=0, column=0, padx=(10, 10), pady=5, sticky='e')
    low_limit_entry = Entry(limits_frame, font=(10), width=15)
    low_limit_entry.grid(row=0, column=1, pady=10,ipady=3,sticky="w")
    # High Limit
    high_limit_label = Label(limits_frame, text='High Limit:', bg=tab_bg, fg='white')
    high_limit_label.grid(row=0, column=2, padx=(10, 10), pady=5, sticky='e')
    high_limit_entry = Entry(limits_frame, font=(10), width=15)
    high_limit_entry.grid(row=0, column=3, pady=10,ipady=3,sticky="w",padx=(0,20))

    # Increase By
    increase_by_label = Label(limits_frame, text='Increase By:', bg=tab_bg, fg='white')
    increase_by_label.grid(row=1, column=0, padx=(10, 10), pady=5, sticky='e')
    increase_by_entry = Entry(limits_frame, font=(10), width=15)
    increase_by_entry.grid(row=1, column=1, pady=10,ipady=3,sticky="w")

    # Max Limit
    max_limit_label = Label(limits_frame, text='Max Limit:', bg=tab_bg, fg='white')
    max_limit_label.grid(row=1, column=2, padx=(10, 10), pady=5, sticky='e')
    max_limit_entry = Entry(limits_frame, font=(10), width=15)
    max_limit_entry.grid(row=1, column=3, pady=10,ipady=3,sticky="w",padx=(0,20))
    
    # PID
    pid_lframe= LabelFrame(ctc_tab,text="PID",fg="white",bg=tab_bg)
    pid_lframe.grid(row=5, column=0, sticky="nesw",padx=120,pady=(20,10))
    # pid_lframe.grid_columnconfigure(0, weight=1)  # Make the first column growable
    # pid_lframe.grid_rowconfigure(5, weight=1)  # Make the first row growable
    
    #PID P
    Label(pid_lframe,text="P",fg="white",bg=tab_bg).grid(row=0,column=0,sticky="ew",padx=(20,20),pady=20)
    ctc_P_entry=Entry(pid_lframe,font=(10),width=10)
    ctc_P_entry.grid(row=0,column=1,pady=0,ipady=3,sticky="ew")
  
    #PID I
    Label(pid_lframe,text="I",fg="white",bg=tab_bg).grid(row=0,column=2,sticky="we",padx=(20,20))
    ctc_I_entry=Entry(pid_lframe,font=(10),width=10)
    ctc_I_entry.grid(row=0,column=3,pady=0,ipady=3,sticky="ew")

    #PID D
    Label(pid_lframe,text="D",fg="white",bg=tab_bg).grid(row=0,column=4,sticky="we",padx=(20,20))
    ctc_D_entry=Entry(pid_lframe,font=(10),width=10)
    ctc_D_entry.grid(row=0,column=5,pady=0,ipady=3,sticky="ew")
    
    #Temprature Controls
    temp_frame = LabelFrame(ctc_tab, text='Temperature Controls', fg='white', bg=tab_bg)
    temp_frame.grid(row=6, column=0, rowspan=2, pady=(20, 10), padx=60, sticky='nwes')
    # temp_frame.grid_rowconfigure(6, weight=1)  # Make the first row growable
    # temp_frame.grid_rowconfigure(7, weight=1)  # Make the first row growable
    # temp_frame.grid_columnconfigure(0, weight=1)  # Make the first row growable
    
    
    

    # Start Temp
    start_temp_label = Label(temp_frame, text='Start Temp:', bg=tab_bg, fg='white')
    start_temp_label.grid(row=0, column=0, padx=30, pady=5, sticky='ew')
    start_temp_entry = Entry(temp_frame, font=(10), width=7)
    start_temp_entry.grid(row=0, column=1, pady=10,ipady=3,sticky="ew")
    
    # Stop Temp
    stop_temp_label = Label(temp_frame, text='Stop Temp:', bg=tab_bg, fg='white')
    stop_temp_label.grid(row=0, column=2, padx=30, pady=5, sticky='ew')
    stop_temp_entry = Entry(temp_frame, font=(10), width=7)
    stop_temp_entry.grid(row=0, column=3, pady=10,ipady=3,sticky="ew")

    # Interval Temp
    interval_label = Label(temp_frame, text='Interval Temp:', bg=tab_bg, fg='white')
    interval_label.grid(row=0, column=4, padx=30, pady=5, sticky='ew')
    interval_entry = Entry(temp_frame, font=(10), width=7)
    interval_entry.grid(row=0, column=5, pady=10,ipady=3,sticky="ew")

    # Threshold
    threshold_label = Label(temp_frame, text='Threshold:', bg=tab_bg, fg='white')
    threshold_label.grid(row=1, column=0, padx=30, pady=5, sticky='ew')
    threshold_entry = Entry(temp_frame, font=(10), width=7)
    threshold_entry.grid(row=1, column=1, pady=10,ipady=3,sticky="ew")
    
    #Delay
    delay_label = Label(temp_frame, text='Avg Delay:', bg=tab_bg, fg='white')
    delay_label.grid(row=1, column=4, padx=30, pady=5, sticky='ew')
    delay_entry = Entry(temp_frame, font=(10), width=7)
    delay_entry.grid(row=1, column=5, pady=10,ipady=3,sticky="ew")
    
    #Complete Cycle
    complete_cycle_var= IntVar()
    Checkbutton(ctc_tab,text="Complete Cycle",fg="white",bg=tab_bg,highlightthickness=0,variable=complete_cycle_var, activebackground=tab_bg, activeforeground='white',selectcolor="black").grid(row=8,column=0,pady=20,sticky="ew")

    
    
  
    ##CURRENT SOURCE TAB##
    # current_source_tab.grid_columnconfigure(0, weight=2)
    # current_source_tab.grid_rowconfigure(0, weight=1)
    # Title
    title_lframe = LabelFrame(current_source_tab, text="Title", fg="white", bg=tab_bg)
    title_lframe.grid(row=0, column=0,rowspan=1, sticky="nsew",padx=250,pady=(40,25))
    # title_lframe.grid_rowconfigure(0, weight=1)  # Make the first row growable
    # title_lframe.grid_columnconfigure(0, weight=1)  # Make the first row growable
    title_entry=Entry(title_lframe,font=(10),width=20)
    title_entry.pack(pady=(0,5),padx=10,ipady=5)
    

    # Drive
    drive_lframe = LabelFrame(current_source_tab, text="Current Controls", fg="white", bg=tab_bg)
    drive_lframe.grid(row=1, column=0, rowspan=3, sticky="nsew",padx=250,pady=25)
    # drive_lframe.grid_rowconfigure(1, weight=1)  # Make the first row growable
    # drive_lframe.grid_columnconfigure(0, weight=1)  # Make the first row growable


    
    current_start_lframe=LabelFrame(drive_lframe,text="Current Start Value (A)",fg="white",bg=tab_bg)
    current_start_lframe.grid(row=0,column=0,padx=10,pady=(5,10),sticky="w")

    current_start_entry=Entry(current_start_lframe,font=(10),width=20)
    current_start_entry.grid(row=0,column=0,rowspan=2,pady=10,padx=10,ipady=5)


    intervalno_lframe=LabelFrame(drive_lframe,text="Number of Current Intervals at a Temperature",fg="white",bg=tab_bg)
    intervalno_lframe.grid(row=1,column=0,padx=10,pady=(5,10),sticky="w")

    intervalno_entry=Entry(intervalno_lframe,font=(10),width=20)
    intervalno_entry.grid(row=0,column=0,rowspan=3,pady=10,padx=10,ipady=5)


    interval_lframe=LabelFrame(drive_lframe,text="Increase Current Interval at a Temperature",fg="white",bg=tab_bg)
    interval_lframe.grid(row=2,column=0,padx=10,pady=(5,10),sticky="w")

    interval_entry=Entry(interval_lframe,font=(10),width=20)
    interval_entry.grid(row=0,column=0,rowspan=3,pady=10,padx=10,ipady=5)
    
        ### other ###
    # root.protocol("WM_DELETE_WINDOW", confirm)
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
    # root.bind("<Configure>", configure_grid)
    root.mainloop()