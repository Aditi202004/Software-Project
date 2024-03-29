
# Required imports for connecting the device
import pyvisa, serial, telnetlib


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
import threading

# Required imports for maintaining the data
import csv, json
import numpy as np


# Required import to make the program sleep
import time


# Required import for Directories of files
from datetime import datetime
from os.path import exists
from os import mkdir


# --- Experiment Variables --- #

# Variables for Instruments...
global NANOVOLTMETER, CURRENT_SOURCE, CTC


# Variables for user input parameters...
global MAX_RETRY, INPUT_CHANNEL_OF_CTC, TOLERANCE, OUTPUT_CHANNEL_OF_CTC, HIGH_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC, THRESHOLD, START_CURRENT, INCREASING_INTERVAL_OF_CURRENT, START_TEMPERATURE, END_TEMPERATURE, DELAY_OF_CTC, INCREASING_INTERVAL_OF_TEMPERATURE, COMPLETE_CYCLE, CSV_FILE

# Array to store resistances at all temperatures...
RESISTANCE_VALUES = [] 


# --- Graph Variables --- #

# Variables for the plotting graph...
global FRAME_FOR_GRAPH, LABEL_FOR_GRAPH, FIGURE_FOR_GRAPH, CANVAS_FOR_GRAPH, GRAPH, ANNOTATION, TOOLBAR_FOR_GRAPH, Y_COORDINATE_OF_LAST_ADDED_POINT, X_COORDINATE_OF_LAST_ADDED_POINT


# Array to store the lines...
ARRAY_OF_PLOTTING_LINES = [] 


settings_file="setting_data.json"
settings={"device_name":"GPIB0::6::INSTR",
"output_dir":"./",
"ctc_address":"192.168.0.2",
"ctc_telnet":"23",
"rs232":"COM 1"}

tab_bg="#575757"
selected_bg="#8a8a8a"


#----------------------------------------- Graph Plotting Part ----------------------------------------------------#

#%%

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
            cont, ind = ARRAY_OF_PLOTTING_LINES.contains(event)
            if cont:
                UPDATE_ANNOTATION(ind, ARRAY_OF_PLOTTING_LINES, annotations)
                annotations.set_visible(True)
                event.canvas.draw_idle()
            else:
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
def ADD_POINT_TO_GRAPH(NEW_X_COORDINATE, NEW_Y_COORDINATE):
    global X_COORDINATE_OF_LAST_ADDED_POINT, Y_COORDINATE_OF_LAST_ADDED_POINT, ARRAY_OF_PLOTTING_LINES, CANVAS_FOR_GRAPH

    PLOTTING_LINE = ARRAY_OF_PLOTTING_LINES[0]
    PLOTTING_LINE.set_data(np.append(PLOTTING_LINE.get_xdata(), NEW_X_COORDINATE), np.append(PLOTTING_LINE.get_ydata(), NEW_Y_COORDINATE))
    # update the view limits as per the newly added points
    GRAPH.relim()
    GRAPH.autoscale_view()
    CANVAS_FOR_GRAPH.draw_idle()
    if(X_COORDINATE_OF_LAST_ADDED_POINT): X_COORDINATE_OF_LAST_ADDED_POINT = NEW_X_COORDINATE
    if(Y_COORDINATE_OF_LAST_ADDED_POINT): Y_COORDINATE_OF_LAST_ADDED_POINT = NEW_Y_COORDINATE


def SET_GRAPH_IN_TAB(GRAPH_TAB):

    global FRAME_FOR_GRAPH, LABEL_FOR_GRAPH, FIGURE_FOR_GRAPH, CANVAS_FOR_GRAPH, GRAPH, ANNOTATION, TOOLBAR_FOR_GRAPH, Y_COORDINATE_OF_LAST_ADDED_POINT, X_COORDINATE_OF_LAST_ADDED_POINT

    FRAME_FOR_GRAPH = GRAPH_TAB 

    LABEL_FOR_GRAPH = tk.Label(FRAME_FOR_GRAPH, text="Resistance Vs. Temperature") # Adding label/title for the graph

    LABEL_FOR_GRAPH.config(font=('Times', 32)) # Changing the default font style and size to Times and 32

    FIGURE_FOR_GRAPH = Figure() # Created a figure to add graph

    CANVAS_FOR_GRAPH = FigureCanvasTkAgg(FIGURE_FOR_GRAPH, master = FRAME_FOR_GRAPH) # Created a canvas to plot graph

    GRAPH = FIGURE_FOR_GRAPH.add_subplot(111)  # Add a subplot with index (e.g., 111) for a single subplot

    GRAPH.set_xlabel("TEMPERATURE") # Set X label
    GRAPH.set_ylabel("RESISTANCE") # Set Y label
    GRAPH.grid() # Added grids to graph
    GRAPH.axhline(linewidth=2, color='black') # Added X axis
    GRAPH.axvline(linewidth=2, color='black') # Added Y axis

    ANNOTATION = GRAPH.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->")) # Annotion means when we hover cursor to a point a small box will appear displaying the x and y co-ordinates

    ANNOTATION.set_visible(False) # Making it invisible initially (We will make it visible when we hover the cursor in DISPLAY_ANNOTATION_WHEN_HOVER Function)

    TOOLBAR_FOR_GRAPH = NavigationToolbar2Tk(CANVAS_FOR_GRAPH, FRAME_FOR_GRAPH) # Added toolbar for graph
    TOOLBAR_FOR_GRAPH.pan() # Made the graph is in pan mode... Simply pan mode is selected... Pan mode means the mode where you can move the graph... (+ kind of symbol in the toolbar)...

    Y_COORDINATE_OF_LAST_ADDED_POINT = None
    X_COORDINATE_OF_LAST_ADDED_POINT = None

    
    PLOTTING_LINE, = GRAPH.plot([], [], color="orange", linestyle="-", marker="o", markerfacecolor="blue", markeredgewidth=1, markeredgecolor="black" ) # Plotted an empty graph...
    ARRAY_OF_PLOTTING_LINES.append(PLOTTING_LINE) # Appending the line(plot) to ARRAY_OF_PLOTTING_LINES...

    ADD_POINT_TO_GRAPH(1,1)
    ADD_POINT_TO_GRAPH(2,2)
    ADD_POINT_TO_GRAPH(3,-1)
    ADD_POINT_TO_GRAPH(4,5)


    # Making zooming, hovering by mouse
    CANVAS_FOR_GRAPH.mpl_connect("key_press_event", lambda event: KEY_PRESS_HANDLER(event, CANVAS_FOR_GRAPH, TOOLBAR_FOR_GRAPH))
    CANVAS_FOR_GRAPH.mpl_connect('scroll_event', ZOOM_INOUT_USING_MOUSE)
    CANVAS_FOR_GRAPH.mpl_connect("motion_notify_event", lambda event: DISPLAY_ANNOTATION_WHEN_HOVER(event, ARRAY_OF_PLOTTING_LINES
    , ANNOTATION))


    # Making Canvas, Label, Frame visible in the tab by packing
    LABEL_FOR_GRAPH.pack()
    CANVAS_FOR_GRAPH.get_tk_widget().pack(fill="both", expand=True)
    FRAME_FOR_GRAPH.pack(fill="both", expand=True)

#%%


#------------------------------------------- Experiment Part ------------------------------------------------------#

#%%

# Function to connect the instruments with software
def CONNECT_INSTRUMENTS(): 
    global NANOVOLTMETER, CURRENT_SOURCE, CTC
    connected=0
    i = 0
    # connecting nanovoltmeter
    while True:
        try:
            rm = pyvisa.ResourceManager()
            NANOVOLTMETER = rm.open_resource('GPIB0::2::INSTR')
            i = 0
            connected+=1
            break
        except:
            if i==MAX_RETRY:
                messagebox.showinfo("Alert","NANOVOLTMETER not connected... check its connection!")
                i = 0
                break
            i+=1

    # connecting current source
    while True:
        try:
            CURRENT_SOURCE = serial.Serial('COM1', baudrate=9600,timeout=10)
            i = 0
            connected+=1
            break
        except:
            if i==MAX_RETRY:
                messagebox.showinfo("Alert","CURRENT SOURCE not connected... check its connection!")
                i = 0
                break
            i+=1

    # connecting CTC
    while True:
        try:
            CTC = telnetlib.Telnet("192.168.0.2",23,10)
            i = 0
            connected+=1
            break
        except:
            if i==MAX_RETRY:
                messagebox.showinfo("Alert","CTC not connected... check its connection!")
                i = 0
                break
            i+=1
    
        return 1
    

    if connected==3: return 1 # if all three devices are connected then return 1
    else: return -1
       

# ----------------------------------------------------- Helper functions for the experiment --------------------------------------------------

# Function to convert the command to correct format, which CTC will understand and sends it to CTC...
def SEND_COMMAND_TO_CTC(command): 
    retry_number = 0 

    while(retry_number < MAX_RETRY):

        try:
            CTC.write((command+'\n').encode())
            return CTC.read_until(b"\n",1).decode('ascii')

        except Exception as e:
            print(f"Error occurred while sending command to CTC: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5) # Adding a short delay before retrying
            
    raise Exception("OOPS!!! Couldn't send command to CTC even after maximun number of tries")
    
# Function to convert the command to correct format, which Current Source will understand and sends it to Current Source...
def SEND_COMMAND_TO_CURRENT_SOURCE(command):

    retry_number = 0 
    while(retry_number < MAX_RETRY):

        try:
            CURRENT_SOURCE.write((command+'\n').encode())
            return CURRENT_SOURCE.readline().decode().strip()

        except Exception as e:
            print(f"Error occurred while sending command to Current Source: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5) # Adding a short delay before retrying
            
    raise Exception("OOPS!!! Couldn't send command to Current Source even after maximum number of tries")

# Function to get the voltage reading from the Nanovoltmeter...
def GET_PRESENT_VOLTAGE_READING():
    global MAX_RETRY
    retry_number = 0 
    while(retry_number < MAX_RETRY):

        try:
            return float(NANOVOLTMETER.query("FETCh?"))

        except Exception as e:
            print(f"Error occurred while sending command to Current Source: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5) # Adding a short delay before retrying
            
    raise Exception("OOPS!!! Couldn't get voltage reading from Nanovoltmeter even after maximum number of tries")

# Function to get the current temperature of sample from ctc...
def GET_PRESENT_TEMPERATURE_OF_CTC():  
    retry_number = 0
    while(retry_number < MAX_RETRY):

        try:
            return float(SEND_COMMAND_TO_CTC('"channel.'+INPUT_CHANNEL_OF_CTC+'?"'))
        
        except Exception as e:
            print(f"Error occurred while getting temperature of CTC: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5) # Adding a short delay before retrying

    raise Exception("Couldn't get temperature from ctc!") 

# Function to Achieve and Stabilize required temperature...
def ACHIEVE_AND_STABILIZE_TEMPERATURE(required_temperature): 
    global HIGH_POWER_LIMIT_OF_CTC 
    print("===> Achieving ", required_temperature, "K...")

    SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.PID.Setpoint" '+str(required_temperature))
    SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.Hi lmt" '+str(HIGH_POWER_LIMIT_OF_CTC))

    retry_number = 0
    temperature_before_stabilizing = GET_PRESENT_TEMPERATURE_OF_CTC()

    lower_bound = required_temperature - THRESHOLD
    upper_bound = required_temperature + THRESHOLD

    while(True):

        time.sleep(3)
        present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

        if lower_bound <= present_temperature <= upper_bound :
            print(required_temperature, " K is achieved but not stabilized...")
            break

        else:
            print("Current Temperature is ", present_temperature, "... Waiting to achieve required temperature ", required_temperature)
            retry_number += 1

        if retry_number == MAX_RETRY : # Increasing the high limit of power if possible...

            if HIGH_POWER_LIMIT_OF_CTC + INCREASE_POWER_LIMIT_OF_CTC <= MAXIMUM_POWER_LIMIT_OF_CTC :

                if present_temperature <= temperature_before_stabilizing :

                    HIGH_POWER_LIMIT_OF_CTC += INCREASE_POWER_LIMIT_OF_CTC
                    SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.Hi lmt" ' + str(HIGH_POWER_LIMIT_OF_CTC))

                    print(required_temperature," K is not achieving by current high power limit of CTC...")
                    print("So, Increased high power limit of CTC by "+str(INCREASE_POWER_LIMIT_OF_CTC)," W...")
                    print("New High power limit of CTC is ",HIGH_POWER_LIMIT_OF_CTC,"...")

                    # We are starting again by increasing high power limit of ctc... So...
                    retry_number = 0 
                    temperature_before_stabilizing = present_temperature

            else:
                raise Exception("Cannot ACHIEVe all the temperatures by given Maximum limit of Power")
            
    print("*************************************************************************")
    print("===> Stabilizing at ", required_temperature, "K...")

    while(True):

        minimum_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()
        maximum_temperature = minimum_temperature
        retry_number = 0

        while(retry_number < MAX_RETRY):

            present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

            print("Current temperature = ", present_temperature, " K")

            if present_temperature > maximum_temperature:
                maximum_temperature = present_temperature
            if present_temperature < minimum_temperature:
                minimum_temperature = present_temperature
            
            time.sleep(10) # Waiting for 10 seconds...

            retry_number += 1

        if maximum_temperature - minimum_temperature < TOLERANCE:
            print(required_temperature, " K is achieved and stabilized...")
            break

        else:
            print("Temperature is not stabilized yet... Retrying...")

# Function to get the current resistance of the sample at current temperature...
def GET_PRESENT_RESISTANCE():

    SEND_COMMAND_TO_CURRENT_SOURCE("OUTP ON") # Switching Current_Source output ON...

    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:COMP 100") # Making Compliance as 100V...

    reading = 0
    present_current = START_CURRENT

    resistance_readings = [] # Array to store resistance values at five different DC Currents...

    while(reading < NUMBER_OF_CURRENT_INTERVALS):

        # Sending command to set the output current to present_current...
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR " + str(present_current))

        time.sleep(5) # Waiting some time...

        # Get the voltage reading...
        positive_cycle_voltage = GET_PRESENT_VOLTAGE_READING()
        resistance_readings.append(positive_cycle_voltage / present_current)

        # Sending command to set the output current to -present_current...
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR -" + str(present_current))

        # Get the voltage reading...
        negative_cycle_voltage = GET_PRESENT_VOLTAGE_READING()
        resistance_readings.append(-1 * negative_cycle_voltage / present_current)


        present_current += INCREASING_INTERVAL_OF_CURRENT
        reading += 1
    
    SEND_COMMAND_TO_CURRENT_SOURCE("OUTP OFF") # Switching Current_Source output OFF
    
    return sum(resistance_readings) / len(resistance_readings)

# Function to write the temperature and resistance values into csv file
def WRITE_DATA_TO_CSV(temperature, resistance):

    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([temperature, resistance])

# Function to get the resistances at all temperatures...
def GET_RESISTANCE_AT_ALL_TEMPERATURES(start_temperature, end_temperature):

    # Switching CTC output ON
    SEND_COMMAND_TO_CTC("outputEnable on")

    # Making direction 1 in forward cycle and -1 in backward cycle...
    direction = 1 if start_temperature <= end_temperature else -1

    present_temperature = start_temperature

    while(present_temperature * direction < end_temperature * direction):

        # Achieving the current temperature... This function is defined above...
        ACHIEVE_AND_STABILIZE_TEMPERATURE(present_temperature) 

        time.sleep(DELAY_OF_CTC) # Delaying some time...

        # Getting current resistance of the sample at current temmperature...
        present_resistance = GET_PRESENT_RESISTANCE() 

        # Writing the present temperature and resistance into csv file...
        WRITE_DATA_TO_CSV(present_temperature, present_resistance)

        present_temperature += INCREASING_INTERVAL_OF_TEMPERATURE * direction


    SEND_COMMAND_TO_CTC("outputEnable off")

# Checks if all given user input values are accurate and sends required msgs to ctc to set some of the values
def CHECK_AND_SET_ALL_VALUES(): 

    global TITLE, MAX_RETRY, INPUT_CHANNEL_OF_CTC, TOLERANCE, OUTPUT_CHANNEL_OF_CTC, HIGH_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC, THRESHOLD, START_CURRENT, NUMBER_OF_CURRENT_INTERVALS, INCREASING_INTERVAL_OF_CURRENT, START_TEMPERATURE, END_TEMPERATURE, DELAY_OF_CTC, INCREASING_INTERVAL_OF_TEMPERATURE, COMPLETE_CYCLE, CSV_FILE

    INPUT_CHANNEL_OF_CTC=input_var.get().replace(" ", "") #to remove space
    OUTPUT_CHANNEL_OF_CTC=output_var.get().replace(" ", "") #to remove space

    #getting ctc data
    try:
        HIGH_POWER_LIMIT_OF_CTC=float(high_limit_entry.get())
        # SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.HiLmt" '+str(HIGH_POWER_LIMIT_OF_CTC))
    except:
        messagebox.showinfo("Alert","Invalid Input for: High Limit !")
        return -1

    try:
        low_val=float(low_limit_entry.get())
        # SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.LowLmt" '+str(low_val))
    except:
        messagebox.showinfo("Alert","Invalid Input for: Low Limit !")
        return -1

    try:
        INCREASE_POWER_LIMIT_OF_CTC=float(increase_by_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Increase By !")
        return -1
    
    try:
        MAXIMUM_POWER_LIMIT_OF_CTC=float(max_limit_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Max Limit !")
        return -1

    try:
        ctc_P_val=float(ctc_P_entry.get())
        # SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.PID.P" '+str(ctc_P_val))
    except:
        messagebox.showinfo("Alert","Invalid Input for P !")
        return -1
    
    try:
        ctc_I_val=float(ctc_I_entry.get())
        # SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.PID.I" '+str(ctc_I_val))
    except:
        messagebox.showinfo("Alert","Invalid Input for I !")
        return -1
    
    try:
        ctc_D_val=float(ctc_D_entry.get())
        # SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.PID.D" '+str(ctc_D_val))
    except:
        messagebox.showinfo("Alert","Invalid Input for D !")
        return -1
    
    try:
        START_TEMPERATURE = float(start_temp_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Start Temp!")
        return -1
    
    try:
        END_TEMPERATURE = float(stop_temp_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Stop Temp!")
        return -1
    
    try:
        INCREASING_INTERVAL_OF_TEMPERATURE = float(interval_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Interval Temp!")
        return -1
    
    try:
        THRESHOLD = float(threshold_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Threshold!")
        return -1
    
    try:
        TOLERANCE = float(tolerance_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Tolerance!")
        return -1
    

    try:
        DELAY_OF_CTC = float(delay_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Avg Delay!")
        return -1
    
    COMPLETE_CYCLE = int(complete_cycle_var.get())

    #getting current source data
    try:
        START_CURRENT=float(current_start_entry.get())
        if START_CURRENT >= 10e-1:
            print("Alert! Enter current value less than 10e-1 !")
            return -1
    except:
        messagebox.showinfo("Alert","Invalid Input for Current Star Value (A)!")
        return -1

    try:
        NUMBER_OF_CURRENT_INTERVALS=int(intervalno_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Number of Current Intervals at a Temperature!")
        return -1
    
    try:
        INCREASING_INTERVAL_OF_CURRENT=float(interval_entry.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Increase Current Interval at a Temperature!")
        return -1

    title_val=title_entry.get()
    invalid_chars=['\\','/',':','*','?','"','<','>','|']
    for c in invalid_chars:
        if c in title_val:
            messagebox.showinfo("Alert",'Invalid Input for: TITLE !\nCannot contain \\ / : * ? " < > |')
            return -1
        TITLE=title_val

    return 1



# ------------------------------------------------------------- trigger functions ---------------------------------------------------------

# Main trigger function where all the functions are called
def TRIGGER():

    global MAX_RETRY, INPUT_CHANNEL_OF_CTC, TOLERANCE, OUTPUT_CHANNEL_OF_CTC, HIGH_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC, THRESHOLD, START_CURRENT, INCREASING_INTERVAL_OF_CURRENT, START_TEMPERATURE, END_TEMPERATURE, DELAY_OF_CTC, INCREASING_INTERVAL_OF_TEMPERATURE, COMPLETE_CYCLE, CSV_FILE

    # Getting resistances from starting temperature to end temperature(forward cycle)... The function is defined above...
    GET_RESISTANCE_AT_ALL_TEMPERATURES(START_TEMPERATURE, END_TEMPERATURE)
    
    if COMPLETE_CYCLE : GET_RESISTANCE_AT_ALL_TEMPERATURES(END_TEMPERATURE, START_TEMPERATURE)

# Function to start trigger in a parallel thread so that interaction with GUI is possible even after trigger event
def START_TRIGGER():
    # if(check_non_sync_values()):
    #     return

    # if(sync_set_config(False,False)!=1):
    #     return

    if(CHECK_AND_SET_ALL_VALUES() == -1): 
        return

    print("all vals checked")
    ControlPanel.select(2)

    
    START_TRIGGER_THREAD()

# starts the triggering thread if all the instruments are connected
def START_TRIGGER_THREAD():
    loading_popup=Toplevel(root) 
    loading_popup.config(bg="black")
    # loading_popup.attributes('-topmost', True)
    loading_popup.geometry(center_geo(200, 60))
    loading_popup.overrideredirect(True)
    loading_popup.resizable(False,False)

    Label(loading_popup,text="Checking Devices...",fg="white",bg="black").place(relx=0.5,rely=0.5,anchor="center")

    loading_popup.grab_set()
    loading_popup.wait_visibility()
    root.update()

    if CONNECT_INSTRUMENTS() == 1:
        loading_popup.destroy()
        root.update() 
        global trigger_thread

        # trigger_btn.config(text="Abort",command=show_abort_trigger_popup,bg=selected_bg)
        trigger_thread=threading.Thread(target=TRIGGER)
        trigger_thread.start()
        
    else:
        loading_popup.destroy()
        root.update()
        messagebox.showinfo("Alert","Could not connect... CHECK ALL CONNECTIONS AND WIRES AND RETRY")
        
    # check_device(loading_popup)
    loading_popup.mainloop()
  

#%%


#-------------------------------------------- Interface Part ----------------------------------------------------#


    
# confirmation before quiting Gui
def confirm(): 
   if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # export_config()
        root.destroy()

# saves all changes made in the settings to the settings.json file
def write_settings(): 
    global settings

    file_handler=open(settings_file, 'w',encoding='utf-8')
    file_handler.write(json.dumps(settings))

# returns center values for any widget according to pc screen
def center_geo(window_width,window_height): 

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))-25

    return "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)
  
# changes the settings value then invokes function to write those changes to the file
def set_settings(key,val): 
    settings[key]=val
    write_settings()

def set_entry(entry_widget,text): # sets the value of any entry/textbox with the given text
    entry_widget.delete(0,'end')
    entry_widget.insert(0,str(text).strip())

# shows popup for choosing output dir and sets the text on label
def ASK_FOR_OUTP_DIR_AND_SHOW_IT(out_dir_label): 
    dirname = filedialog.askdirectory()
    if dirname:
        settings["output_dir"]=dirname
        write_settings()
        out_dir_label.config(text=dirname)


### popup window functions ###
        
# destroys popup & invokes given callback function afterwards
def CLOSE_POPUP(popup,callback=None): 
    popup.destroy()
    root.update()
    if(callback!=None):
        callback()


# function to update the val of global variable MAX_RETRY
def UPDATE_MAX_RETRY(widget):
    global MAX_RETRY
    MAX_RETRY = widget.get()
    set_entry(widget, widget.get())


# checks for valid output directory, else resets the output directory to same as GUI location
def SET_DEFAULT_DIR(): 
    if(not exists(settings["output_dir"])):
        settings["output_dir"]="./"
        write_settings()


# shows settings popup
def POPUP_SETTINGS_AND_UPDATE_THEM(): 
    global ctc_address_entry,ctc_telnet_entry

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

    # Button(settings_popup,text="⟳").grid(row=0,column=1,padx=(120,0),pady=(10,5)) #command=lambda: get_gpib_devices(device_options)

    ctc_address_var = StringVar(value=settings["ctc_address"])

    Label(settings_popup,text="CTC Address:",fg="white",bg=tab_bg).grid(row=2,column=0,sticky="e",padx=(0,10),pady=10)
    ctc_address_entry=Entry(settings_popup,font=(10),width=15,textvariable=ctc_address_var)
    ctc_address_entry.grid(row=2,column=1,pady=0,sticky="w")
    ctc_address_entry.bind("<KeyRelease>",lambda x: set_settings("ctc_address",ctc_address_var.get())) #updates ctc_adress on any key release event

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
    max_retry_entry.bind("<KeyRelease>",lambda x: UPDATE_MAX_RETRY(max_retry_entry))

    Label(settings_popup,text="Output Directory:",fg="white",bg=tab_bg).grid(row=6,column=0,sticky="e",padx=(0,10),pady=10)
    out_dir_label=Label(settings_popup,text=settings["output_dir"],anchor="w",width=25,fg="white",bg=tab_bg)
    out_dir_label.grid(row=6,column=1,sticky="w",padx=(0,10),pady=10)
    Button(settings_popup,text="Select Folder",command=lambda: ASK_FOR_OUTP_DIR_AND_SHOW_IT(out_dir_label)).grid(row=6,column=1,padx=(150,0),pady=10)

    settings_popup.protocol("WM_DELETE_WINDOW", lambda : CLOSE_POPUP(settings_popup))
    settings_popup.grab_set()
    settings_popup.mainloop()


# shows popup containing all three device names
def show_info_popup(re_query=False): 
    try:
        d_info="Nanovoltmeter Device: "+ str(NANOVOLTMETER) + "\nCurrent Source Device:" + str(CURRENT_SOURCE) + "\nCTC Device: " + str(CTC)
        messagebox.showinfo("Device Info",d_info)
    except:
        CONNECT_INSTRUMENTS()
        if(not re_query):
            show_info_popup(True)
        else:
            messagebox.showinfo("Alert! ", "Not able to connect instruments... check code")


### graph functions ###



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

    settings_btn= Button(side_bar_frame,text="Settings",height= 2,command=POPUP_SETTINGS_AND_UPDATE_THEM)
    settings_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    info_btn= Button(side_bar_frame,text="Info",height= 2,command=show_info_popup)
    info_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    sync_set_btn= Button(side_bar_frame,text="Sync Set",height= 2)
    sync_set_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    sync_get_btn= Button(side_bar_frame,text="Sync Get",height= 2)
    sync_get_btn.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    trigger_btn= Button(side_bar_frame,text="Trigger",height=2, command=START_TRIGGER)
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
   
    # Input Selection
    io_frame = LabelFrame(ctc_tab, bg=tab_bg, borderwidth=0, highlightthickness=0)
    io_frame.grid(row=0, column=0, rowspan=3, pady=(20, 10), padx=120, sticky='nwes')
    
    input_label = Label(io_frame, text='Input:', bg=tab_bg, fg='white')
    input_label.grid(row=0, column=0,sticky="ew",padx=(20,20),pady=20)

    input_options = ['In 1', 'In 2', 'In 3', 'In 4']
    input_var = StringVar()
    input_dropdown = ttk.Combobox(io_frame, textvariable=input_var, values=input_options, state='readonly')
    input_dropdown.grid(row=0,column=1,rowspan=3,sticky="ew",pady=(10,10))
    input_dropdown.current(0)

    # Output Selection
    output_label = Label(io_frame, text='Output:', bg=tab_bg, fg='white')
    output_label.grid(row=0, column=2,sticky="ew",padx=(20,20),pady=20)

    output_options = ['Out 1', 'Out 2']
    output_var = StringVar()
    output_dropdown = ttk.Combobox(io_frame, textvariable=output_var, values=output_options, state='readonly')
    output_dropdown.grid(row=0, column=3,rowspan=3,sticky="ew",pady=(10,10))
    
    output_dropdown.current(1)
    
    #default values
    default_low_limit = "0"
    default_high_limit = "4"
    default_increase_by = "1"
    default_max_limit = "7"
    default_pid_P = "30"
    default_pid_I = "0.5"
    default_pid_D = "120"
    default_start_temp = "305"
    default_stop_temp = "315"
    default_interval_temp = "5"
    default_threshold = "0.5"
    default_tolerance="0.3"
    default_delay = "30"
    default_title = "Default Title"
    default_current_start = "10e-5"
    default_intervalno = "5"
    default_interval = "10e-6"

    limits_frame = LabelFrame(ctc_tab, text='Power Controls', fg='white', bg=tab_bg)
    limits_frame.grid(row=3, column=0, rowspan=2, pady=(20, 10), padx=120, sticky='nwes')

    # Low Limit
    low_limit_label = Label(limits_frame, text='Low Limit:', bg=tab_bg, fg='white')
    low_limit_label.grid(row=0, column=0, padx=(10, 10), pady=5, sticky='e')
    low_limit_entry = Entry(limits_frame, font=(10), width=15)
    low_limit_entry.grid(row=0, column=1, pady=10, ipady=3, sticky="w")
    low_limit_entry.insert(0, default_low_limit)

    # High Limit
    high_limit_label = Label(limits_frame, text='High Limit:', bg=tab_bg, fg='white')
    high_limit_label.grid(row=0, column=2, padx=(10, 10), pady=5, sticky='e')
    high_limit_entry = Entry(limits_frame, font=(10), width=15)
    high_limit_entry.grid(row=0, column=3, pady=10, ipady=3, sticky="w", padx=(0, 20))
    high_limit_entry.insert(0, default_high_limit)

    # Increase By
    increase_by_label = Label(limits_frame, text='Increase By:', bg=tab_bg, fg='white')
    increase_by_label.grid(row=1, column=0, padx=(10, 10), pady=5, sticky='e')
    increase_by_entry = Entry(limits_frame, font=(10), width=15)
    increase_by_entry.grid(row=1, column=1, pady=10, ipady=3, sticky="w")
    increase_by_entry.insert(0, default_increase_by)

    # Max Limit
    max_limit_label = Label(limits_frame, text='Max Limit:', bg=tab_bg, fg='white')
    max_limit_label.grid(row=1, column=2, padx=(10, 10), pady=5, sticky='e')
    max_limit_entry = Entry(limits_frame, font=(10), width=15)
    max_limit_entry.grid(row=1, column=3, pady=10, ipady=3, sticky="w", padx=(0, 20))
    max_limit_entry.insert(0, default_max_limit)

    # PID
    pid_lframe= LabelFrame(ctc_tab,text="PID",fg="white",bg=tab_bg)
    pid_lframe.grid(row=5, column=0, sticky="nesw",padx=120,pady=(20,10))

    #PID P
    Label(pid_lframe,text="P",fg="white",bg=tab_bg).grid(row=0,column=0,sticky="ew",padx=(20,20),pady=20)
    ctc_P_entry=Entry(pid_lframe,font=(10),width=10)
    ctc_P_entry.grid(row=0,column=1,pady=0,ipady=3,sticky="ew")
    ctc_P_entry.insert(0, default_pid_P)

    #PID I
    Label(pid_lframe,text="I",fg="white",bg=tab_bg).grid(row=0,column=2,sticky="we",padx=(20,20))
    ctc_I_entry=Entry(pid_lframe,font=(10),width=10)
    ctc_I_entry.grid(row=0,column=3,pady=0,ipady=3,sticky="ew")
    ctc_I_entry.insert(0, default_pid_I)

    #PID D
    Label(pid_lframe,text="D",fg="white",bg=tab_bg).grid(row=0,column=4,sticky="we",padx=(20,20))
    ctc_D_entry=Entry(pid_lframe,font=(10),width=10)
    ctc_D_entry.grid(row=0,column=5,pady=0,ipady=3,sticky="ew")
    ctc_D_entry.insert(0, default_pid_D)

    #Temperature Controls
    temp_frame = LabelFrame(ctc_tab, text='Temperature Controls', fg='white', bg=tab_bg)
    temp_frame.grid(row=6, column=0, rowspan=2, pady=(20, 10), padx=60, sticky='nwes')

    # Start Temp
    start_temp_label = Label(temp_frame, text='Start Temp:', bg=tab_bg, fg='white')
    start_temp_label.grid(row=0, column=0, padx=30, pady=5, sticky='ew')
    start_temp_entry = Entry(temp_frame, font=(10), width=7)
    start_temp_entry.grid(row=0, column=1, pady=10, ipady=3, sticky="ew")
    start_temp_entry.insert(0, default_start_temp)

    # Stop Temp
    stop_temp_label = Label(temp_frame, text='Stop Temp:', bg=tab_bg, fg='white')
    stop_temp_label.grid(row=0, column=2, padx=30, pady=5, sticky='ew')
    stop_temp_entry = Entry(temp_frame, font=(10), width=7)
    stop_temp_entry.grid(row=0, column=3, pady=10, ipady=3, sticky="ew")
    stop_temp_entry.insert(0, default_stop_temp)

    # Interval Temp
    interval_label = Label(temp_frame, text='Interval Temp:', bg=tab_bg, fg='white')
    interval_label.grid(row=0, column=4, padx=30, pady=5, sticky='ew')
    interval_entry = Entry(temp_frame, font=(10), width=7)
    interval_entry.grid(row=0, column=5, pady=10, ipady=3, sticky="ew")
    interval_entry.insert(0, default_interval_temp)

    # Threshold
    threshold_label = Label(temp_frame, text='Threshold:', bg=tab_bg, fg='white')
    threshold_label.grid(row=1, column=0, padx=30, pady=5, sticky='ew')
    threshold_entry = Entry(temp_frame, font=(10), width=7)
    threshold_entry.grid(row=1, column=1, pady=10, ipady=3, sticky="ew")
    threshold_entry.insert(0, default_threshold)

    # Tolerance
    tolerance_label = Label(temp_frame, text='Tolerance:', bg=tab_bg, fg='white')
    tolerance_label.grid(row=1, column=2, padx=30, pady=5, sticky='ew')
    tolerance_entry = Entry(temp_frame, font=(10), width=7)
    tolerance_entry.grid(row=1, column=3, pady=10, ipady=3, sticky="ew")
    tolerance_entry.insert(0, default_tolerance)

    # Delay
    delay_label = Label(temp_frame, text='Avg Delay:', bg=tab_bg, fg='white')
    delay_label.grid(row=1, column=4, padx=30, pady=5, sticky='ew')
    delay_entry = Entry(temp_frame, font=(10), width=7)
    delay_entry.grid(row=1, column=5, pady=10, ipady=3, sticky="ew")
    delay_entry.insert(0, default_delay)

    # Complete Cycle
    complete_cycle_var = IntVar()
    Checkbutton(ctc_tab, text="Complete Cycle", fg="white", bg=tab_bg, highlightthickness=0, variable=complete_cycle_var, activebackground=tab_bg, activeforeground='white', selectcolor="black").grid(row=8, column=0, pady=20, sticky="ew")

    # Title
    title_lframe = LabelFrame(current_source_tab, text="Title", fg="white", bg=tab_bg)
    title_lframe.grid(row=0, column=0, rowspan=1, sticky="nsew", padx=250, pady=(40, 25))

    title_entry = Entry(title_lframe, font=(10), width=20)
    title_entry.pack(pady=(0, 5), padx=10, ipady=5)
    title_entry.insert(0, default_title)

    # Drive
    drive_lframe = LabelFrame(current_source_tab, text="Current Controls", fg="white", bg=tab_bg)
    drive_lframe.grid(row=1, column=0, rowspan=3, sticky="nsew", padx=250, pady=25)

    current_start_lframe = LabelFrame(drive_lframe, text="Current Start Value (A)", fg="white", bg=tab_bg)
    current_start_lframe.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")

    current_start_entry = Entry(current_start_lframe, font=(10), width=20)
    current_start_entry.grid(row=0, column=0, rowspan=2, pady=10, padx=10, ipady=5)
    current_start_entry.insert(0, default_current_start)

    intervalno_lframe = LabelFrame(drive_lframe, text="Number of Current Intervals at a Temperature", fg="white", bg=tab_bg)
    intervalno_lframe.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")

    intervalno_entry = Entry(intervalno_lframe, font=(10), width=20)
    intervalno_entry.grid(row=0, column=0, rowspan=3, pady=10, padx=10, ipady=5)
    intervalno_entry.insert(0, default_intervalno)

    interval_lframe = LabelFrame(drive_lframe, text="Increase Current Interval at a Temperature", fg="white", bg=tab_bg)
    interval_lframe.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

    interval_entry = Entry(interval_lframe, font=(10), width=20)
    interval_entry.grid(row=0, column=0, rowspan=3, pady=10, padx=10, ipady=5)
    interval_entry.insert(0, default_interval)
    # Setup the graph_tab...
    SET_GRAPH_IN_TAB(graph_tab)

        ### other ###
    root.protocol("WM_DELETE_WINDOW", confirm)
    root.wait_visibility()
    root.update()
    
    root_width=root.winfo_width()
    root_height=root.winfo_height()
    root.geometry(center_geo(root_width,root_height))
    root.minsize(root_width,root_height)

    CONNECT_INSTRUMENTS()
    SET_DEFAULT_DIR()
    root.mainloop()

