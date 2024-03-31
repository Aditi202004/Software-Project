#### By Sai Pranay Deep, Aditi Wekhande, Devanshi Chhatbar, Saket Meshram, Jay Solanki.... ####

# Note :- We have used Ethernet cable for CTC device, GPIB cable for Nanovoltmeter, RS232 cable for AC/DC current source. The code may change if you use different cables... :)


# Required imports for connecting the device
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


####---------------------------------------- Graph Plotting Part ----------------------------------------------####

# Array to store the lines...
ARRAY_OF_PLOTTING_LINES = [] 
ARRAY_OF_PLOTTING_LINES_R_vs_Time=[]
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
            for line in ARRAY_OF_PLOTTING_LINES:
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
def ADD_POINT_TO_GRAPH(NEW_X_COORDINATE, NEW_Y_COORDINATE):
    global X_COORDINATE_OF_LAST_ADDED_POINT, Y_COORDINATE_OF_LAST_ADDED_POINT, ARRAY_OF_PLOTTING_LINES, CANVAS_OF_GRAPH

    PLOTTING_LINE = ARRAY_OF_PLOTTING_LINES[0]
    PLOTTING_LINE.set_data(np.append(PLOTTING_LINE.get_xdata(), NEW_X_COORDINATE), np.append(PLOTTING_LINE.get_ydata(), NEW_Y_COORDINATE))
    # update the view limits as per the newly added points
    GRAPH.relim()
    GRAPH.autoscale_view()
    CANVAS_OF_GRAPH.draw_idle()
    if(X_COORDINATE_OF_LAST_ADDED_POINT): X_COORDINATE_OF_LAST_ADDED_POINT = NEW_X_COORDINATE
    if(Y_COORDINATE_OF_LAST_ADDED_POINT): Y_COORDINATE_OF_LAST_ADDED_POINT = NEW_Y_COORDINATE


# 
def ADD_POINT_TO_GRAPH_R_vs_Time(NEW_X_COORDINATE, NEW_Y_COORDINATE, selected_temperature):
    global ARRAY_OF_PLOTTING_LINES, CANVAS_OF_GRAPH
    # global selected_temperature
    # Find the plotting line corresponding to the selected temperature
    for line in ARRAY_OF_PLOTTING_LINES:
        if line.get_label() == selected_temperature:
            PLOTTING_LINE = line
            break

    # Append the new data points to the plotting line
    PLOTTING_LINE.set_data(np.append(PLOTTING_LINE.get_xdata(), NEW_X_COORDINATE), np.append(PLOTTING_LINE.get_ydata(), NEW_Y_COORDINATE))
    
    # Update the view limits as per the newly added points
    GRAPH.relim()
    GRAPH.autoscale_view()
    CANVAS_OF_GRAPH.draw_idle()


# Function to save the graph plot image to selected directory...
def SAVE_THE_GRAPH_INTO(directory):
    IMAGE_FILE_NAME = "Plot of "+ TITLE + ".png"
    GRAPH_IMAGE_PATH = os.path.join(directory, IMAGE_FILE_NAME)
    CANVAS_OF_GRAPH.figure.savefig(GRAPH_IMAGE_PATH)


#
def SET_R_vs_Temp_Graph(GRAPH_TAB_R_vs_Time):

    global FRAME_OF_GRAPH, LABEL_OF_GRAPH, FIGURE_OF_GRAPH, CANVAS_OF_GRAPH, GRAPH, ANNOTATION, TOOLBAR_OF_GRAPH, Y_COORDINATE_OF_LAST_ADDED_POINT, X_COORDINATE_OF_LAST_ADDED_POINT
    global temperature_combobox

    FRAME_OF_GRAPH = tb.Frame(GRAPH_TAB_R_vs_Time) 

    LABEL_OF_GRAPH = tk.Label(FRAME_OF_GRAPH, text = "Resistance Vs. Temperature") # Adding label/title for the graph

    LABEL_OF_GRAPH.config(font=('Times', 25)) # Changing the default font style and size to Times and 32
    # temperature_combobox = ttk.Combobox(FRAME_OF_GRAPH, font=("Arial", 10), state='readonly')
    # temperature_combobox.current(0)

    # FIGURE_OF_GRAPH = Figure(figsize=(5, 4)) # Created a figure to add graph

    # CANVAS_OF_GRAPH = FigureCanvasTkAgg(FIGURE_OF_GRAPH, master = FRAME_OF_GRAPH) # Created a canvas to plot graph
    # FRAME_OF_GRAPH = tb.Frame(GRAPH_TAB) 

    FIGURE_OF_GRAPH = Figure(figsize=(6, 5))  # Adjust the figsize parameter to set a smaller figure size (e.g., 4x3 inches)

    CANVAS_OF_GRAPH = FigureCanvasTkAgg(FIGURE_OF_GRAPH, master=FRAME_OF_GRAPH)
   


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

    Y_COORDINATE_OF_LAST_ADDED_POINT = None
    X_COORDINATE_OF_LAST_ADDED_POINT = None

    
    PLOTTING_LINE, = GRAPH.plot([], [], color="orange", linestyle="-", marker="o", markerfacecolor="blue", markeredgewidth=1, markeredgecolor="black" ) # Plotted an empty graph...
    ARRAY_OF_PLOTTING_LINES.append(PLOTTING_LINE) # Appending the line(plot) to ARRAY_OF_PLOTTING_LINES...


    # Making zooming, hovering by mouse
    CANVAS_OF_GRAPH.mpl_connect("key_press_event", lambda event: KEY_PRESS_HANDLER(event, CANVAS_OF_GRAPH, TOOLBAR_OF_GRAPH))
    CANVAS_OF_GRAPH.mpl_connect('scroll_event', ZOOM_INOUT_USING_MOUSE)
    CANVAS_OF_GRAPH.mpl_connect("motion_notify_event", lambda event: DISPLAY_ANNOTATION_WHEN_HOVER(event, ARRAY_OF_PLOTTING_LINES
    , ANNOTATION))


    # Making Canvas, Label, Frame visible in the tab by packing
    LABEL_OF_GRAPH.pack()
    # temperature_combobox.pack(padx=10, pady=10)
    CANVAS_OF_GRAPH.get_tk_widget().pack()
    FRAME_OF_GRAPH.pack()


#
def SET_R_vs_Time_Graph(GRAPH_TAB_R_vs_Time):
    global FRAME_OF_GRAPH_R_vs_Time, LABEL_OF_GRAPH_R_vs_Time, FIGURE_OF_GRAPH_R_vs_Time, CANVAS_OF_GRAPH_R_vs_Time, GRAPH_R_vs_Time, TOOLBAR_OF_GRAPH_R_vs_Time, Y_COORDINATE_OF_LAST_ADDED_POINT_R_vs_Time, X_COORDINATE_OF_LAST_ADDED_POINT_R_vs_Time
    global temperature_combobox
    global selected_temperature

    # FRAME_OF_GRAPH_R_vs_Time = tb.Frame(GRAPH_TAB) 
    FRAME_OF_GRAPH_R_vs_Time = tb.Frame(GRAPH_TAB_R_vs_Time) 

    LABEL_OF_GRAPH_R_vs_Time = tk.Label(FRAME_OF_GRAPH_R_vs_Time, text="Current Temperature :") 
    LABEL_OF_GRAPH_R_vs_Time.config(font=('Times', 20)) # Adding label/title for the graph
    temperature_combobox = tb.Combobox(FRAME_OF_GRAPH_R_vs_Time, font=("Arial", 10), state='readonly')
    # Function to update label with combobox value
    def update_label(*args):
        selected_temperature = temperature_combobox.get()
        
        LABEL_OF_GRAPH_R_vs_Time.config(text="Current Temperature : " + selected_temperature+ " K")
        
        # Check if plotting line already exists for the selected temperature
        plotting_line_exists = False
        for line in ARRAY_OF_PLOTTING_LINES_R_vs_Time:
            if line.get_label() == selected_temperature:
                plotting_line_exists = True
                break
        
        # If plotting line doesn't exist, create a new one
        if not plotting_line_exists:
            new_plotting_line, = GRAPH_R_vs_Time.plot([], [], linestyle="-", marker="o")
            new_plotting_line.set_label(selected_temperature)
            ARRAY_OF_PLOTTING_LINES_R_vs_Time.append(new_plotting_line)
        # Adjusting the limits of x and y axes to display in the first quadrant only
        GRAPH_R_vs_Time.set_xlim(0, None)  # X-axis starts from 0 and extends towards positive infinity
        GRAPH_R_vs_Time.set_ylim(0, None)  # Y-axis starts from 0 and extends towards positive infinity
        
        CANVAS_OF_GRAPH_R_vs_Time.draw_idle()
    # Associate the update_label function with the combobox
    temperature_combobox.bind("<<ComboboxSelected>>", update_label)
    FIGURE_OF_GRAPH_R_vs_Time = Figure(figsize=(6, 4.5))  # Adjust the figsize parameter to set a smaller figure size (e.g., 4x3 inches)
    CANVAS_OF_GRAPH_R_vs_Time = FigureCanvasTkAgg(FIGURE_OF_GRAPH_R_vs_Time, master=FRAME_OF_GRAPH_R_vs_Time)
    GRAPH_R_vs_Time = FIGURE_OF_GRAPH_R_vs_Time.add_subplot(111)  # Add a subplot with index (e.g., 111) for a single subplot
    GRAPH_R_vs_Time.set_xlabel("TIME") # Set X label
    GRAPH_R_vs_Time.set_ylabel("RESISTANCE") # Set Y label
    GRAPH_R_vs_Time.grid() # Added grids to graph
    GRAPH_R_vs_Time.axhline(linewidth=2, color='black') # Added X axis
    GRAPH_R_vs_Time.axvline(linewidth=2, color='black') # Added Y axis
    TOOLBAR_OF_GRAPH_R_vs_Time = NavigationToolbar2Tk(CANVAS_OF_GRAPH_R_vs_Time, FRAME_OF_GRAPH_R_vs_Time) # Added toolbar for graph
    TOOLBAR_OF_GRAPH_R_vs_Time.pan() # Made the graph is in pan mode... Simply pan mode is selected... Pan mode means the mode where you can move the graph... (+ kind of symbol in the toolbar)...
    Y_COORDINATE_OF_LAST_ADDED_POINT_R_vs_Time = None
    X_COORDINATE_OF_LAST_ADDED_POINT_R_vs_Time = None
    ARRAY_OF_PLOTTING_LINES_R_vs_Time = []  # Initialize array to hold plotting lines
    # Making zooming, hovering by mouse
    CANVAS_OF_GRAPH_R_vs_Time.mpl_connect("key_press_event", lambda event: KEY_PRESS_HANDLER(event, CANVAS_OF_GRAPH_R_vs_Time, TOOLBAR_OF_GRAPH_R_vs_Time))
    CANVAS_OF_GRAPH_R_vs_Time.mpl_connect('scroll_event', ZOOM_INOUT_USING_MOUSE)
    # Making Canvas, Label, Frame visible in the tab by packing
    temperature_combobox.pack(padx=10, pady=(30,20))
    LABEL_OF_GRAPH_R_vs_Time.pack(pady=(0,0))
    CANVAS_OF_GRAPH_R_vs_Time.get_tk_widget().pack()
    FRAME_OF_GRAPH_R_vs_Time.pack()


####---------------------------------------- Experiment Part --------------------------------------------------####

# Function to check whether all the instruments are connected or not...
def CONNECT_INSTRUMENTS(): 
    global CURRENT_SOURCE, CTC

    number_of_connected_devices = 0
    retry_number = 0

    # Connecting Current source to PC...
    while True:
        try:
            rm = pyvisa.ResourceManager()
            CURRENT_SOURCE = rm.open_resource(SETTINGS["device_name"])
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showerror("Alert","CURRENT_SOURCE(6221) is not connected to PC... Check its connections!!")
                retry_number = 0
                break
            retry_number += 1

    # Connecting CTC to PC...
    while True:
        try:
            CTC = telnetlib.Telnet(host = SETTINGS["CTC_Address"], port = int(SETTINGS["Telnet_Port"]), timeout = 10)
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showerror("Alert","CTC is not connected to PC... Check its connections!")
                retry_number = 0
                break
            retry_number += 1
    
    # Checking whether Nanovoltmeter is connected to Current Source or not...
    while True:
        try:
            # Checking by sending the commands to Nanovoltmeter via Current Source...
            SEND_COMMAND_TO_CURRENT_SOURCE('SYST:COMM:SER:SEND “*IDN?”')
            SEND_COMMAND_TO_CURRENT_SOURCE('SYST:COMM:SER:ENT?')
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showerror("Alert","NANOVOLTMETER(2182A) is not connected to CURRENT SOURCE(6221)... Check its connections!")
                retry_number = 0
                break
            retry_number += 1

    
    # Returning True if all three devices are connected, otherwise False
    if number_of_connected_devices == 3: 
        return True 
    else: 
        return False


# Arrays to store input channels and output channels and the stored below are just default, these will be changed in SYNC_GET function defined below...
INPUT_CHANNELS_LIST_OF_CTC = ['In 1', 'In 2', 'In 3', 'In 4']
OUTPUT_CHANNELS_LIST_OF_CTC = ['Out 1', 'Out 2']

# Function to take data from CTC, save it in config_data.json and display it on the GUI...
def SYNC_GET():
    
    if CONNECT_INSTRUMENTS():

        ## Syncing CTC data ##
        CHANNELS_LIST = SEND_COMMAND_TO_CTC('channel.list?').split("., ")

        # Clearing the default channels before appending actual channels...
        INPUT_CHANNELS_LIST_OF_CTC.clear() 
        OUTPUT_CHANNELS_LIST_OF_CTC.clear()

        INPUT_CHANNELS_LIST_OF_CTC = [channel for channel in CHANNELS_LIST if channel.startswith('I')]
        OUTPUT_CHANNELS_LIST_OF_CTC = [channel for channel in CHANNELS_LIST if not channel.startswith('I')]

        if ENTRY_OF_INPUT_CHANNEL.get() == "":
            ENTRY_OF_INPUT_CHANNEL.set(INPUT_CHANNELS_LIST_OF_CTC[0])
        if ENTRY_OF_OUTPUT_CHANNEL.get() == "":
            ENTRY_OF_OUTPUT_CHANNEL.set(OUTPUT_CHANNELS_LIST_OF_CTC[0])

        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_LOW_POWER_LIMIT, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get()+'.LowLmt?"'))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_HIGH_POWER_LIMIT, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get()+'.HiLmt?"'))

        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_P_VALUE_OF_CTC, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get() + '.PID.P?"'))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_I_VALUE_OF_CTC, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get() + '.PID.I?"'))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_D_VALUE_OF_CTC, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get() + '.PID.D?"'))

        ## Syncing CURRENT SOURCE data ##

        # For Resistance vs Time 
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_HIGH_PULSE, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:HIGH?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_LOW_PULSE, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:LOW?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_PULSE_WIDTH, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:WIDT?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:INT?"))

        # For Resistance vs Temperature 
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_START_CURRENT, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STAR?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_STOP_CURRENT, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STOP?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STEP?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:COUN?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_DELAY_OF_CURRENT_SOURCE, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:DEL?"))


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
            return CURRENT_SOURCE.query(command)

        except Exception as e:
            print(f"Error occurred while sending command to Current Source: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5) # Adding a short delay before retrying
            
    raise Exception("OOPS!!! Couldn't send command to Current Source even after maximum number of tries")


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

    print("*************************************************************************")
    print("===> Achieving", required_temperature, "K...")


    SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.PID.Setpoint" '+str(required_temperature)) # Setting the setpoint of CTC to required_temperature...

    retry_number = 0
    temperature_before_stabilizing = GET_PRESENT_TEMPERATURE_OF_CTC()
    # initial_temperature_difference = required_temperature - temperature_before_stabilizing

    lower_bound = required_temperature - THRESHOLD
    upper_bound = required_temperature + THRESHOLD

    time_elapsed = 0

    while not TO_ABORT:

        time.sleep(3)
        time_elapsed+=3
        present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

        if lower_bound <= present_temperature <= upper_bound :
            print(required_temperature, "K is achieved but not stabilized...")
            break

        else:
            print("Current Temperature is", present_temperature, "... Waiting to achieve required temperature ", required_temperature, "K...")
            if abs(present_temperature - temperature_before_stabilizing) < 0.03*time_elapsed: # 0.04 is the max ramp rate currently set in CTC 
                retry_number += 1
            else: retry_number = 0                

        if retry_number == 10 : # Increasing the high limit of power if possible...

            if HIGH_POWER_LIMIT_OF_CTC + INCREASE_POWER_LIMIT_OF_CTC <= MAXIMUM_POWER_LIMIT_OF_CTC :

                if present_temperature <= temperature_before_stabilizing :

                    HIGH_POWER_LIMIT_OF_CTC += INCREASE_POWER_LIMIT_OF_CTC
                    SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.HiLmt" ' + str(HIGH_POWER_LIMIT_OF_CTC))

                    print(required_temperature," K is not achieving by current high power limit of CTC...")
                    print("So, Increased high power limit of CTC by "+str(INCREASE_POWER_LIMIT_OF_CTC)," W...")
                    print("New High power limit of CTC is ", HIGH_POWER_LIMIT_OF_CTC,"...")

                    # We are starting again by increasing high power limit of ctc... So...
                    retry_number = 0 
                    temperature_before_stabilizing = present_temperature

            else:
                messagebox.showwarning("Alert","Cannot Achieve all the temperatures by given Maximum limit of Power!!")
                raise Exception("Cannot Achieve all the temperatures by given Maximum limit of Power")

    if TO_ABORT: return


    print("______________________________________________________________________")
    print("===> Stabilizing at", required_temperature, "K...")

    while not TO_ABORT:

        minimum_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()
        maximum_temperature = minimum_temperature
        retry_number = 0

        while not TO_ABORT and retry_number < MAX_RETRY:

            present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

            print("Current temperature =", present_temperature, " K")

            if present_temperature > maximum_temperature: maximum_temperature = present_temperature
            if present_temperature < minimum_temperature: minimum_temperature = present_temperature
            
            time.sleep(10) # Waiting for 10 seconds...

            retry_number += 1

        if TO_ABORT: return

        if maximum_temperature - minimum_temperature < TOLERANCE:
            print(required_temperature, " K is achieved and stabilized...")
            break

        else:
            print("Temperature is not stabilized yet... Retrying...")


# Function to get resistance at a particular instant...
def GET_RESISTANCES():
    # The data received from the current source is a string having resistances and time stamps... Eg:4.2Ω,0.00s,4.3Ω,0.01s,...\n
    # Collect all data (resistance and time) in string format
    data = SEND_COMMAND_TO_CURRENT_SOURCE("TRACE:DATA?")[:-1]  # Remove trailing newline(\n)

    # Split the string and store in an array in {resistance, time} repetition
    data = list(map(float, data.split(",")))

    # Separate resistances and time stamps using list slicing
    resistance_readings = data[::2]
    time_stamps = data[1::2]

    return resistance_readings, time_stamps


# Function to get current average resistance(Using to get resistance at a temperature in Resistance vs Temperature)...
def GET_PRESENT_RESISTANCE():
    # We are doing this by using Pulse Sweep Step...
    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:SWE ON") # ON the sweeping mode
    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:ARM") # Arming the pulse mode
    SEND_COMMAND_TO_CURRENT_SOURCE("INIT:IMM") # Triggering the pulse mode

    # Wait for some time until it calculates the resistances
    # This value is set by our observations after many trials
    for i in range(NUMBER_OF_CURRENT_INTERVALS + 0.5):
        if TO_ABORT:
            return -1
        time.sleep(1)

    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:ABOR") # Aborting the sweep process

    resistance_readings, = GET_RESISTANCES()

    return sum(resistance_readings) / len(resistance_readings)


# Function to get resistances with time at a temperature(Used in Resistance vs Time at a temperature)...
def GET_RESISTANCES_WITH_TIME_AT(temperature):
    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:SWE OFF") # OFF the sweeping mode
    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:ARM") # Arming the 
    SEND_COMMAND_TO_CURRENT_SOURCE(("INIT:IMM")) # triggering

    time.sleep(1.5) # time required to execute above three commands by the device

    present_time = 0
    index_of_last_update = 0

    present_csvfile = TITLE + "_Resistance_vs_Time_at_" + temperature + ".csv"
    while present_time <= MEASURING_TIME:
        if TO_ABORT:
            break
        present_time += 5
        time.sleep(5)
        resistance_readings, time_stamps = GET_RESISTANCES()

        WRITE_DATA_TO(present_csvfile, time_stamps[index_of_last_update:], resistance_readings[index_of_last_update:])
        # code to save to csv and plot the points in resistance_readings and time_stamps in that graph of that temperature
        index_of_last_update = len(resistance_readings)

    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:ABOR") # stops the sweeping process


# Function to write the temperature and resistance values into csv file
def WRITE_DATA_TO(filename, TemperatureOrTimes, resistances):
    filepath = os.path.join(SETTINGS["Directory"], filename)
    
    with open(filepath, 'a', newline='') as csvfile:  # Open file in write mode
        writer = csv.writer(csvfile)
        for TemperatureOrTime, resistance in zip(TemperatureOrTimes, resistances):
            writer.writerow([TemperatureOrTime, resistance])


# Function to get the resistances at all temperatures...
def GET_RESISTANCE_AT_ALL_TEMPERATURES(direction):

    SEND_COMMAND_TO_CTC("outputEnable on") # Switching CTC output ON
    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:COMP 100") # Making Compliance as 100V...

    filename = TITLE + "_Resistance_vs_Temperature.csv" 

    for present_temperature in ARRAY_OF_ALL_TEMPERATURES[::direction]:
        # Achieving the current temperature... This function is defined above...
        ACHIEVE_AND_STABILIZE_TEMPERATURE(present_temperature) 

        for i in range(DELAY_OF_CTC): # Delaying some time...
            if TO_ABORT: break  
            time.sleep(1) 

        present_resistance = GET_PRESENT_RESISTANCE()
        print("Resistance of the sample is", present_resistance, "Ohm, at temperature", present_temperature, "K...")

        WRITE_DATA_TO(filename, [present_temperature], [present_resistance])
        ADD_POINT_TO_GRAPH(present_temperature, present_resistance)

        if direction and (present_temperature in ARRAY_OF_SELECTED_TEMPERATURES):
            GET_RESISTANCES_WITH_TIME_AT(present_temperature)
    

    SEND_COMMAND_TO_CTC("outputEnable off") # Switching CTC output OFF



# Function to check whether the input values given by the user are in correct data types and are in correct range or not.. If they are correct the value will be set to the devices..
def CHECK_AND_SET_ALL_VALUES(): 

    global INPUT_CHANNEL_OF_CTC, OUTPUT_CHANNEL_OF_CTC
    global HIGH_POWER_LIMIT_OF_CTC, LOW_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC
    global P_VALUE_OF_CTC, I_VALUE_OF_CTC, D_VALUE_OF_CTC
    global START_TEMPERATURE, END_TEMPERATURE, INCREASING_INTERVAL_OF_TEMPERATURE, TOLERANCE, THRESHOLD, DELAY_OF_CTC
    global TITLE
    global START_CURRENT, STOP_CURRENT, NUMBER_OF_CURRENT_INTERVALS, INCREASING_INTERVAL_OF_CURRENT, DELAY_OF_CURRENT_SOURCE
    global MEASURING_TIME, HIGH_PULSE, LOW_PULSE, PULSE_WIDTH, NUMBER_OF_PULSES_PER_SECOND

    # Assigning the parameters of CTC given by user to the variables and Setting those to CTC if they are in correct format...

    INPUT_CHANNEL_OF_CTC = ENTRY_OF_INPUT_CHANNEL.get().replace(" ", "") # Converting In 1, In 2,... as In, In,..., Because CTC takes the input channel whithout spaces...

    OUTPUT_CHANNEL_OF_CTC = ENTRY_OF_OUTPUT_CHANNEL.get().replace(" ", "") # Converting Out 1, Out 2,... as Out1, Out2,..., Because CTC takes the output channel whithout spaces...

    try:
        HIGH_POWER_LIMIT_OF_CTC = float(ENTRY_OF_HIGH_POWER_LIMIT.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.HiLmt" ' + str(HIGH_POWER_LIMIT_OF_CTC)) 
    except:
        messagebox.showwarning("Alert","Invalid Input for: High Limit !")
        return False

    try:
        LOW_POWER_LIMIT_OF_CTC = float(ENTRY_OF_LOW_POWER_LIMIT.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.LowLmt" ' + str(LOW_POWER_LIMIT_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for: Low Limit !")
        return False

    try:
        INCREASE_POWER_LIMIT_OF_CTC = float(ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Increase By !")
        return False
    
    try:
        MAXIMUM_POWER_LIMIT_OF_CTC = float(ENTRY_OF_MAXIMUM_POWER_LIMIT.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Max Limit !")
        return False

    try:
        P_VALUE_OF_CTC = float(ENTRY_OF_P_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.P" ' + str(P_VALUE_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for P !")
        return False
    
    try:
        I_VALUE_OF_CTC = float(ENTRY_OF_I_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.I" ' + str(I_VALUE_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for I !")
        return False
    
    try:
        D_VALUE_OF_CTC = float(ENTRY_OF_D_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.D" ' + str(D_VALUE_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for D !")
        return False
    
    try:
        START_TEMPERATURE = float(ENTRY_OF_START_TEMPERATURE.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Start Temp!")
        return False
    
    try:
        END_TEMPERATURE = float(ENTRY_OF_STOP_TEMPERATURE.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Stop Temp!")
        return False
    
    try:
        INCREASING_INTERVAL_OF_TEMPERATURE = float(ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Interval Temp!")
        return False
    
    try:
        THRESHOLD = float(ENTRY_OF_THRESHOLD.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Threshold!")
        return False
    
    try:
        TOLERANCE = float(ENTRY_OF_TOLERANCE.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Tolerance!")
        return False
    
    try:
        DELAY_OF_CTC = float(ENTRY_OF_DELAY_OF_CTC.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Avg Delay!")
        return False


    # Assigning the parameters of Current Source given by user to the variables if they are in correct format...

    try:
        START_CURRENT = float(ENTRY_OF_START_CURRENT.get())
        if START_CURRENT >= 1:
            messagebox.showwarning("Alert!", "Enter the Current value less than 1 Ampere !")
            return False
    except:
        messagebox.showwarning("Alert","Invalid Input for Start Current Value!")
        return False
    
    try:
        STOP_CURRENT = float(ENTRY_OF_STOP_CURRENT.get())
        if not STOP_CURRENT < 1:
            messagebox.showwarning("Alert!", "Enter the Current value less than 1 Ampere !")
            return False
    except:
        messagebox.showwarning("Alert","Invalid Input for Start Current Value!")
        return False

    try:
        NUMBER_OF_CURRENT_INTERVALS = int(ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Number of Current Intervals at a Temperature!")
        return False
    
    try:
        INCREASING_INTERVAL_OF_CURRENT = float(ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Increase Current Interval at a Temperature!")
        return False

    try:
        DELAY_OF_CURRENT_SOURCE = float(ENTRY_OF_DELAY_OF_CURRENT_SOURCE.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Avg Delay!")
        return False

    try:
        HIGH_PULSE = float(ENTRY_OF_HIGH_PULSE.get())
        if abs(HIGH_PULSE) > 105e-3:
            messagebox.showwarning("Alert!", "Enter the High Pulse in range [-105e-3 to 105e-3] A!")
            return False
    except:
        messagebox.showwarning("Alert","Invalid Input for High Pulse Value!")
        return False
    
    try:
        LOW_PULSE = float(ENTRY_OF_LOW_PULSE.get())
        if abs(LOW_PULSE) > 105e-3:
            messagebox.showwarning("Alert!", "Enter the Low Pulse in range [-105e-3 to 105e-3] A!")
            return False
    except:
        messagebox.showwarning("Alert","Invalid Input for Low Pulse Value!")
        return False
    
    try:
        PULSE_WIDTH = float(ENTRY_OF_PULSE_WIDTH.get())
        if PULSE_WIDTH > 12e-3 or PULSE_WIDTH < 50e-6:
            messagebox.showwarning("Alert!", "Enter the Pulse Width in range [50e-6 to 12e-3] A!")
            return False
    except:
        messagebox.showwarning("Alert","Invalid Input for Pulse Width Value!")
        return False
    
    try:
        NUMBER_OF_PULSES_PER_SECOND = float(ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND.get())
        if NUMBER_OF_PULSES_PER_SECOND > 12 or NUMBER_OF_PULSES_PER_SECOND < 1:
            messagebox.showwarning("Alert!", "Enter the Pulse Interval in range [1 to 12] A!")
            return False
    except:
        messagebox.showwarning("Alert","Invalid Input for Pulse Width Value!")
        return False
    

    # The title should not consists the following invalid characters...
    invalid_characters=['\\','/',':','*','?','"','<','>','|']
    TITLE = ENTRY_OF_TITLE.get() + " " + datetime.now().strftime('%H_%M_%S %d-%B-%Y')

    if TITLE == "" : messagebox.showwarning("Alert",'No input is given for Title!')
    for Character in invalid_characters:
        if Character in TITLE:
            TITLE = None
            messagebox.showwarning("Alert",'Invalid Input for Title !\nCannot contain \\ / : * ? " < > |')
            return False

    return True


# Function to merge two sorted arrays...
def MERGE_BOTH_TEMPERATURES(arr1, arr2):
    final_arr = []
    n = len(arr1)
    m = len(arr2)
    i = 0
    j = 0
    while i<n or j<m :
        if (i<n and j>=m) or ((i<n and j<m) and (arr1[i] <= arr2[j])) :
            final_arr.append(arr1[i])
            i+=1
        elif (i>=n and j<m) or ((i<n and j<m) and (arr1[i] > arr2[j])) :
            final_arr.append(arr2[j])
            j+=1
    
    return final_arr


# Function to start the Experiment...
def START_EXPERIMENT():
    global ARRAY_OF_ALL_TEMPERATURES, ARRAY_OF_SELECTED_TEMPERATURES
    if int(TEMPERATURE_EXPERIMENT.get()):
        curr_temp = START_TEMPERATURE
        while curr_temp <= END_TEMPERATURE:
            ARRAY_OF_ALL_TEMPERATURES.append(curr_temp)
            curr_temp += INCREASING_INTERVAL_OF_TEMPERATURE
            
    if int(TIME_EXPERIMENT.get()):
        ARRAY_OF_SELECTED_TEMPERATURES = temperature_combobox["values"]
        ARRAY_OF_SELECTED_TEMPERATURES.sort()  # sorting the array
        ARRAY_OF_ALL_TEMPERATURES = MERGE_BOTH_TEMPERATURES(ARRAY_OF_ALL_TEMPERATURES, ARRAY_OF_SELECTED_TEMPERATURES)


    if not TO_ABORT:
        # Getting resistances from starting temperature to end temperature(forward cycle)... The function is defined above...
        GET_RESISTANCE_AT_ALL_TEMPERATURES(1)
    
    # If experiment is aborted then the function will break
    if TO_ABORT: 
        print("ABORTED !")
        TRIGGER_BUTTON.config(text= "Trigger", command=TRIGGER)
        INTERFACE.update()
        return
    
    if not TO_ABORT and int(TEMPERATURE_EXPERIMENT.get()) and int(COMPLETE_CYCLE.get()):
        GET_RESISTANCE_AT_ALL_TEMPERATURES(-1)
        
    # If experiment is aborted then the function will break
    if TO_ABORT: 
        print("ABORTED !")
        TRIGGER_BUTTON.config(text= "Trigger", command=TRIGGER)
        INTERFACE.update()
        return
    
    if not TO_ABORT:
        SAVE_THE_GRAPH_INTO(SETTINGS["Directory"]) # Saving the Image of plot into required directory...
        print("Experiment is completed successfully! (Graph and data file are stored in the chosen directory)")


# Function to trigger the Experiment... 
def TRIGGER():

    if CONNECT_INSTRUMENTS():
        if CHECK_AND_SET_ALL_VALUES(): # Checking and Setting all values...

            CONTROL_PANEL.select(2) # Displaying Graph tab when experiment is started...

            print("Checking Devices....")
            Thread(target = START_EXPERIMENT).start() # Starting the experiment and threading to make GUI accessable even after the experiment is start... 


# Function to abort the experiment
def ABORT_TRIGGER():
    global TO_ABORT
    TO_ABORT = True

    is_armed = int(SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:ARM?"))
    if is_armed:
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:ABOR")

    print("Aborted!")

    TRIGGER_BUTTON.config(text= "Trigger", command=TRIGGER)
    INTERFACE.update()



####---------------------------------------- Interface Part -------------------------------------------------####

# Function to Confirm the user before quiting Interface...
def CONFIRM_TO_QUIT(): 
   if messagebox.askokcancel("Quit", "Are you Sure!! \nDo you want to quit?"):
        # export_config()
        INTERFACE.destroy()


# Function to display entry in a widget
def DISPLAY_VALUE_IN_ENTRY_BOX(entry_box, value):
    entry_box.delete(0,'end')
    entry_box.insert(0,str(value).strip())


# Function to write the settings of the devices into json file...
def WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE(): 
    file_handler=open("SETTINGS.json", 'w',encoding='utf-8')
    file_handler.write(json.dumps(SETTINGS))


# Function to get the geometry of the widget to set at the center...
def CENTER_THE_WIDGET(window_width,window_height): 

    screen_width = INTERFACE.winfo_screenwidth()
    screen_height = INTERFACE.winfo_screenheight()

    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))-25

    return "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)


# Function to destroy the widget...
def CLOSE_WIDGET(widget): 
    widget.destroy()
    INTERFACE.update()


# Function to open filedialog to select the directory...
def OPEN_FILEDIALOG(LABEL_OF_OUTPUT_DIRECTORY): 
    directory = filedialog.askdirectory()
    if directory:
        SETTINGS["Directory"] = directory
        WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE()
        LABEL_OF_OUTPUT_DIRECTORY.config(text = directory)


# Function to display the requirements widget...
def DISPLAY_REQUIREMENTS():
    REQUIREMENTS_WIDGET = Toplevel(INTERFACE)

    REQUIREMENTS_WIDGET.title("Make Sure")
    REQUIREMENTS_WIDGET_Temp_width = int(INTERFACE.winfo_width() / 2)
    REQUIREMENTS_WIDGET_Temp_height = int(INTERFACE.winfo_height() / 1.75)
    REQUIREMENTS_WIDGET.geometry(CENTER_THE_WIDGET(REQUIREMENTS_WIDGET_Temp_width, REQUIREMENTS_WIDGET_Temp_height))
    REQUIREMENTS_WIDGET.resizable(False, False)
    REQUIREMENTS_WIDGET.grid_columnconfigure(0, weight=1)
    REQUIREMENTS_WIDGET.grid_columnconfigure(1, weight=1)
    title = Label(REQUIREMENTS_WIDGET, text="Make Sure the Following ")
    title.grid(row=0, column=0, sticky="wens", pady=(10, 10))
    title.config(font=("Times New Roman", 15, "bold"))

    label_text = """
    • GPIB: current source to CPU
    • RS-232: male-to-male between current source and 
      voltmeter 
    • Trigger Link Cable: between current source and voltmeter
    • Telnet: CTC to CPU
    • set GPIB interface for current source
    • set RS-232 interface for nanovoltmeter
    • baudrate of nanovoltmeter and current source should be 
      19.2K and flow control on nanovoltmeter: NONE
    """
    label = Text(REQUIREMENTS_WIDGET, wrap='word', height=10, width=50)
    label.insert('1.0', label_text)
    label.config(state='disabled')
    label.grid(row=1, column=0, sticky="wens", pady=(0, 10))
    label.config(font=("Times New Roman", 12))

    def confirm_connections():
        REQUIREMENTS_WIDGET.destroy()

    Button(REQUIREMENTS_WIDGET, text="Confirm", font=("Arial", 12, "bold"), bd=2, command=confirm_connections).grid(row=3, column=0, padx=(15, 0), pady=20)

    REQUIREMENTS_WIDGET.protocol("WM_DELETE_WINDOW", lambda: CLOSE_WIDGET(REQUIREMENTS_WIDGET))
    REQUIREMENTS_WIDGET.transient(INTERFACE)
    REQUIREMENTS_WIDGET.grab_set()
    INTERFACE.wait_window(REQUIREMENTS_WIDGET)

# Function for getting what experiments user wants to do from user...
def DISPLAY_SELECTING_EXPERIMENTS_WIDGET(): 
    global TIME_EXPERIMENT, TEMPERATURE_EXPERIMENT

    # Creating Settings Widget...
    SELECTING_EXP_WIDGET = Toplevel(INTERFACE)
    SELECTING_EXP_WIDGET_Temp_width = int(INTERFACE.winfo_width() / 2)
    SELECTING_EXP_WIDGET_Temp_height = int(INTERFACE.winfo_height() / 2.7)
    SELECTING_EXP_WIDGET.title("Experiment Settings")
    SELECTING_EXP_WIDGET.geometry(CENTER_THE_WIDGET(SELECTING_EXP_WIDGET_Temp_width, SELECTING_EXP_WIDGET_Temp_height))
    SELECTING_EXP_WIDGET.resizable(False,False)
    SELECTING_EXP_WIDGET.grid_columnconfigure(0, weight=1)
    SELECTING_EXP_WIDGET.grid_columnconfigure(1, weight=1)
   
    label = Label(SELECTING_EXP_WIDGET, text = "Choose the experiment(s) you want to perform : ", fg = "white", bg = "#575757")
    label.grid(row = 0,column = 0,  sticky = "we",  pady = 25)
    label.config(font = ("Arial", 12, "bold"))
    
    TIME_EXPERIMENT = IntVar()
    Checkbutton(SELECTING_EXP_WIDGET, text = "Resistance vs Time at specific temperatures", fg = "white", bg = "#575757", highlightthickness = 0, variable = TIME_EXPERIMENT, activebackground = "#575757", activeforeground = 'white', selectcolor = "black", font=("Arial", 10)).grid(row = 1, column = 0,  sticky = "w", pady = 10,padx=(60,0))

    TEMPERATURE_EXPERIMENT = IntVar()
    Checkbutton(SELECTING_EXP_WIDGET, text = "Resistance vs Temperature", fg = "white", bg = "#575757", highlightthickness = 0, variable = TEMPERATURE_EXPERIMENT, activebackground = "#575757", activeforeground = 'white', selectcolor = "black", font=("Arial", 10)).grid(row = 2, column = 0,  sticky = "w", pady = 10,padx=(60,0))
    
    def confirm_settings():
        if TIME_EXPERIMENT.get() == 1 and TEMPERATURE_EXPERIMENT.get() == 0:
            CONTROL_PANEL.hide(GRAPH_R_vs_Temp)
            CONTROL_PANEL.hide(CURRENT_SOURCE_TAB)
            FRAME_OF_TEMPERATURE_CONTROLS.grid_forget()
            COMPLETE_CYCLE.set(0)  # Uncheck the checkbox
            COMPLETE_CYCLE_CHECKBUTTON.grid_forget()
            SELECTING_EXP_WIDGET.destroy()


        elif TEMPERATURE_EXPERIMENT.get() == 1 and TIME_EXPERIMENT.get() == 0:
            CONTROL_PANEL.hide(GRAPH_R_vs_Time_final)
            CONTROL_PANEL.hide(TEMPERATURE_TAB)
            CONTROL_PANEL.hide(GRAPH_R_vs_Time)

            SELECTING_EXP_WIDGET.destroy()

        else:
            SELECTING_EXP_WIDGET.destroy()
          
    Button(SELECTING_EXP_WIDGET, text="Confirm", font=("Arial", 12, "bold"), bd=2, command=confirm_settings).grid(row=3, column=0, padx=(70,0), pady=20)
    
    
    SELECTING_EXP_WIDGET.protocol("WM_DELETE_WINDOW", lambda : CLOSE_WIDGET(SELECTING_EXP_WIDGET))
    SELECTING_EXP_WIDGET.grab_set()
    SELECTING_EXP_WIDGET.mainloop()


# Function to Create and Open Settings Widget and saving the changes if any are done in this widget...
def OPEN_SETTINGS_WIDGET(): 

    # Creating Settings Widget...
    SETTINGS_WIDGET = Toplevel(INTERFACE)
    SETTINGS_WIDGET.title("Settings")
    SETTINGS_WIDGET_width=int(INTERFACE.winfo_width()/2)
    SETTINGS_WIDGET_height=int(INTERFACE.winfo_height()/2.5)
    SETTINGS_WIDGET.geometry(CENTER_THE_WIDGET(SETTINGS_WIDGET_width,SETTINGS_WIDGET_height))
    SETTINGS_WIDGET.resizable(False,False)
    SETTINGS_WIDGET.grid_columnconfigure(0,weight=1)
    SETTINGS_WIDGET.grid_columnconfigure(1,weight=1)
    Label(SETTINGS_WIDGET, text = "Nanovoltmeter :", fg = "white", bg = "#575757").grid(row = 1, column = 0, rowspan = 2, sticky = "e", padx = (0,10), pady = 10)

    ENTRY_OF_DEVICE = StringVar(value = SETTINGS["device_name"]) # Assigning the variable with the cabel which is in settings (Simply setting default)
    cabels_available = pyvisa.ResourceManager().list_resources()

    DROPDOWN_OF_GPIB_DEVICE = ttk.Combobox(SETTINGS_WIDGET, width = 27,textvariable = ENTRY_OF_DEVICE, values = cabels_available, state = "readonly")
    DROPDOWN_OF_GPIB_DEVICE.bind('<<ComboboxSelected>>', lambda x: SET_SETTINGS("device_name", DROPDOWN_OF_GPIB_DEVICE.get()))
    DROPDOWN_OF_GPIB_DEVICE.grid(row = 0, column = 1, sticky = "w", pady = 10)

    # Creating an entry field to enter the address of the CTC device...
    Label(SETTINGS_WIDGET,text = "CTC Address:", fg = "white", bg = "#575757").grid(row = 2, column = 0, sticky = "e", padx = (0,10), pady = 10)

    VARIABLE_OF_CTC_ADDRESS = StringVar(value = SETTINGS["CTC_Address"]) # Assigning the variable with the address which is in settings (Simply setting default)

    ENTRY_OF_CTC_ADDRESS = Entry(SETTINGS_WIDGET, font = (10), width = 15, textvariable = VARIABLE_OF_CTC_ADDRESS)
    ENTRY_OF_CTC_ADDRESS.grid(row = 2, column = 1, pady = 0, sticky = "w")
    ENTRY_OF_CTC_ADDRESS.bind("<KeyRelease>", lambda x: SET_SETTINGS("CTC_Address", VARIABLE_OF_CTC_ADDRESS.get())) #updates ctc_adress on any key release event


    # Creating an entry field to enter the CTC Telnet...
    Label(SETTINGS_WIDGET, text = "Telnet Port :", fg = "white", bg = "#575757").grid(row = 3, column = 0, sticky = "e", padx = (0,10), pady = 10)

    VARIABLE_OF_TELNET_PORT = StringVar(value = SETTINGS["Telnet_Port"])

    ENTRY_OF_TELNET_PORT = Entry(SETTINGS_WIDGET, font = (10), width = 15, textvariable = VARIABLE_OF_TELNET_PORT)
    ENTRY_OF_TELNET_PORT.grid(row = 3, column = 1, pady = 0, sticky = "w")
    ENTRY_OF_TELNET_PORT.bind("<KeyRelease>",lambda x: SET_SETTINGS("Telnet_Port", VARIABLE_OF_TELNET_PORT.get()))
    

    # Creating an entry field to enter the port of RS232 cabel connected to AC/DC Current Source...
    Label(SETTINGS_WIDGET, text = "RS232_Port :", fg = "white", bg = "#575757").grid(row = 4, column = 0, sticky = "e", padx = (0,10), pady = 10)

    VARIABLE_OF_RS232_PORT = StringVar(value = SETTINGS["RS232_Port"])

    ENTRY_OF_RS232_PORT = Entry(SETTINGS_WIDGET, font = (10), width = 15, textvariable = VARIABLE_OF_RS232_PORT)
    ENTRY_OF_RS232_PORT.grid(row = 4, column = 1, pady = 0, sticky = "w")
    ENTRY_OF_RS232_PORT.bind("<KeyRelease>", lambda x: SET_SETTINGS("RS232_Port", VARIABLE_OF_RS232_PORT.get()))

    # Creating an entry field to enter the Max_retry number...
    Label(SETTINGS_WIDGET, text = "Max_Retry :", fg = "white", bg = "#575757").grid(row = 5, column = 0, sticky = "e", padx = (0,10), pady = 10)

    VARIABLE_OF_MAX_RETRY = StringVar(value = SETTINGS["max_retry"])

    ENTRY_OF_MAX_RETRY = Entry(SETTINGS_WIDGET, font = (10), width = 10, textvariable = VARIABLE_OF_MAX_RETRY)
    ENTRY_OF_MAX_RETRY.grid(row = 5, column = 1, pady = 0, sticky = "w")
    ENTRY_OF_MAX_RETRY.bind("<KeyRelease>", lambda x: SET_SETTINGS("max_retry", VARIABLE_OF_MAX_RETRY.get()))

    # Creating a dialougebox for selecting the directory...
    Label(SETTINGS_WIDGET, text = "Directory:", fg = "white", bg = "#575757").grid(row = 6, column = 0, sticky = "e", padx = (0,10), pady = 10)
    LABEL_OF_OUTPUT_DIRECTORY = Label(SETTINGS_WIDGET,text = SETTINGS["Directory"], anchor = "w", width = 25, fg = "white", bg = "#575757")
    LABEL_OF_OUTPUT_DIRECTORY.grid(row = 6, column = 1, sticky = "w", padx = (0,10), pady = 10)
    Button(SETTINGS_WIDGET, text = "Select Folder", command = lambda: OPEN_FILEDIALOG(LABEL_OF_OUTPUT_DIRECTORY)).grid(row = 6, column = 1, padx = (150,0), pady = 10)
 
    Button(SETTINGS_WIDGET,text="Confirm", font=("Arial", 12, "bold"), bd=2).grid(row =7 , column = 1 ,sticky="w",pady = 20)

    SETTINGS_WIDGET.protocol("WM_DELETE_WINDOW", lambda : CLOSE_WIDGET(SETTINGS_WIDGET))
    SETTINGS_WIDGET.grab_set()
    SETTINGS_WIDGET.mainloop()



# Function to display the info of devices...
def SHOW_INFO_OF_DEVICES(): 

    if CONNECT_INSTRUMENTS() :
        SEND_COMMAND_TO_CURRENT_SOURCE('SYST:COMM:SER:SEND “*IDN?”')
        info_of_nanovoltmeter = SEND_COMMAND_TO_CURRENT_SOURCE('SYST:COMM:SER:ENT?')
        info_of_current_source = str(SEND_COMMAND_TO_CURRENT_SOURCE("*IDN?"))
        info_of_ctc = str(SEND_COMMAND_TO_CTC("description?"))

        info_of_devices = "Nanovoltmeter :" + info_of_nanovoltmeter + "\nCurrent Source :" + info_of_current_source + "\n\nCTC Device: " + info_of_ctc

        messagebox.showinfo("Device Info", info_of_devices)
        

# Function to sync the settings from settings.json file to entry boxes(GUI)...
def SYNC_SETTINGS():
    global SETTINGS, MAX_RETRY
    if exists("SETTINGS.json"):
        with open("SETTINGS.json", "r") as file:
            SETTINGS = json.load(file)

    else:
        SETTINGS = {"device_name":"GPIB0::6::INSTR",
                    "Directory":"./",
                    "CTC_Address":"192.168.0.2",
                    "Telnet_Port":"23",
                    "RS232_Port":"COM1",
                    "max_retry":"10"
                    }  # If the file doesn't exist, initialize SETTINGS some default values
        WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE()

    MAX_RETRY = int(SETTINGS["max_retry"])


# Function to change the settings...
def SET_SETTINGS(key,val): 
    SETTINGS[key] = val
    WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE()
    

def UPDATE_COMBOBOX(event):
    global temperature_combobox
   
    # Get the content of the Text widget
    input_text = TEMPERATURES_ENTRY.get("1.0", "end-1c")
    
    # Split the input_text into individual values based on comma
    values = input_text.split(",")

    # Strip leading and trailing whitespaces from each value
    values = [value.strip() for value in values if value.strip()]  # Include placeholder text
    # Filter out non-numeric values
    numeric_values = [value for value in values if value.replace('.', '', 1).isdigit()]

    # # Populate the Combobox with the extracted values
    # temperature_combobox['values'] = values
    # Populate the Combobox with the extracted numeric values
    temperature_combobox['values'] = numeric_values



if __name__=="__main__":
    global INTERFACE 

    ## Creating a Tkinter Interface ##
    INTERFACE = tb.Window(themename="yeti") # Made a root Interface
    INTERFACE.wm_title("TD-Controller") # Set title to the interface widget
    # INTERFACE.geometry("1000x700") # Set Geometry of the interface widget
    INTERFACE.grid_columnconfigure(0, weight=1) 
    INTERFACE.grid_rowconfigure(0, weight=1)
    INTERFACE.grid_columnconfigure(1, weight=0) 
    

    # Creating a Sidebar and adding Trigger, Settings, Info, Sync Set, Sync Get buttons ## 
    SIDE_BAR = tb.Frame(INTERFACE,bootstyle="info")
    SIDE_BAR.grid(row=0, column=1, rowspan=2, sticky="nswe")

    SETTINGS_BUTTON = Button(SIDE_BAR, text = "Settings", height = 2, command = OPEN_SETTINGS_WIDGET)
    SETTINGS_BUTTON.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    INFO_BUTTON = Button(SIDE_BAR, text = "Info", height = 2, command = SHOW_INFO_OF_DEVICES)
    INFO_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)

    SYNC_SET_BUTTON = Button(SIDE_BAR, text = "Sync Set", height= 2)
    SYNC_SET_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)

    SYNC_GET_BUTTON=Button(SIDE_BAR, text = "Sync Get", height = 2)
    SYNC_GET_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)

    TRIGGER_BUTTON = Button(SIDE_BAR, text = "Trigger", height = 2, command = TRIGGER)
    TRIGGER_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)

    global TO_ABORT
    TO_ABORT = False

    ## Creating Control Panel and adding CTC tab, Current Source tab and Graph tab ##
    CONTROL_PANEL = tb.Notebook(INTERFACE,bootstyle="primary")

    CTC_TAB = tb.Frame(CONTROL_PANEL) 
    CURRENT_SOURCE_TAB = tb.Frame(CONTROL_PANEL) 
    TEMPERATURE_TAB = tb.Frame(CONTROL_PANEL)
    GRAPH_R_vs_Temp = tb.Frame(CONTROL_PANEL) 
    GRAPH_R_vs_Time_final  = tb.Frame(CONTROL_PANEL) 

    CONTROL_PANEL.add(CTC_TAB, text = ' CTC\n Setup ')
    CONTROL_PANEL.add(CURRENT_SOURCE_TAB , text = ' Current Source\n      Setup ')
    CONTROL_PANEL.add(TEMPERATURE_TAB, text = ' Temperature\n Setup ')
    CONTROL_PANEL.add(GRAPH_R_vs_Temp, text = ' Graph\n (R vs Temp) ')
    CONTROL_PANEL.add(GRAPH_R_vs_Time_final , text = ' Graph\n (R vs Time) ')
    CONTROL_PANEL.grid(row = 0, column = 0, sticky = "nswe")
   
   

    ## Creating Dropdowns for selecting input and output channels of CTC...
    FRAME_OF_CHANNELS_SELECTION = LabelFrame(CTC_TAB, text = "Input/Output Channel", bg = "#575757", fg = "white")
    FRAME_OF_CHANNELS_SELECTION.grid(row = 0, column = 0, rowspan = 3, pady = (20, 10), padx = 120, sticky = 'nwes')
    
    # Input Channel
    LABEL_OF_INPUT_CHANNEL = Label(FRAME_OF_CHANNELS_SELECTION, text = 'Input Channel:', bg = "#575757", fg = 'white')
    LABEL_OF_INPUT_CHANNEL.grid(row = 0, column = 0, sticky = "ew", padx = (20,20), pady = 20)

    input_options = ['In 1', 'In 2', 'In 3', 'In 4']
    ENTRY_OF_INPUT_CHANNEL = StringVar()

    DROPDOWN_OF_INPUT_CHANNEL = ttk.Combobox(FRAME_OF_CHANNELS_SELECTION, textvariable = ENTRY_OF_INPUT_CHANNEL,  values = input_options, state = 'readonly')
    DROPDOWN_OF_INPUT_CHANNEL.grid(row = 0, column = 1, rowspan = 3, sticky = "ew", pady = (10,10))
    DROPDOWN_OF_INPUT_CHANNEL.current(0)

    # Output Channel
    LABEL_OF_OUTPUT_CHANNEL = Label(FRAME_OF_CHANNELS_SELECTION, text = 'Output Channel:', bg = "#575757",  fg = 'white')
    LABEL_OF_OUTPUT_CHANNEL.grid(row = 0, column = 2, sticky = "ew", padx = (20,20), pady = 20)

    output_options = ['Out 1', 'Out 2']
    ENTRY_OF_OUTPUT_CHANNEL = StringVar()

    DROPDOWN_OF_OUTPUT_CHANNEL = ttk.Combobox(FRAME_OF_CHANNELS_SELECTION, textvariable = ENTRY_OF_OUTPUT_CHANNEL, values = output_options, state = 'readonly')
    DROPDOWN_OF_OUTPUT_CHANNEL.grid(row = 0, column = 3, rowspan = 3, sticky = "ew", pady = (10,10))
    DROPDOWN_OF_OUTPUT_CHANNEL.current(1)
    

    ## Creating entry fields for Power controls of CTC...
    FRAME_OF_POWER_CONTROLS = LabelFrame(CTC_TAB, text = 'Power Controls', fg = 'white', bg = "#575757")
    FRAME_OF_POWER_CONTROLS.grid(row = 3, column = 0, rowspan = 2, pady = (20, 10), padx = 120, sticky = 'nwes')

    # Low Power Limit entry
    LABEL_OF_LOW_POWER_LIMIT = Label(FRAME_OF_POWER_CONTROLS, text = 'Low Limit(W) :', bg = "#575757", fg = 'white')
    LABEL_OF_LOW_POWER_LIMIT.grid(row = 0, column = 0, padx = (10, 10), pady = 5, sticky = 'e')
    ENTRY_OF_LOW_POWER_LIMIT = Entry(FRAME_OF_POWER_CONTROLS, font = (10), width = 15)
    ENTRY_OF_LOW_POWER_LIMIT.grid(row = 0, column = 1, padx = (10, 10), pady = 10, ipady = 3, sticky = "w")

    # High Power Limit entry
    LABEL_OF_HIGH_POWER_LIMIT = Label(FRAME_OF_POWER_CONTROLS, text = 'High Limit(W) :', bg = "#575757", fg = 'white')
    LABEL_OF_HIGH_POWER_LIMIT.grid(row = 0, column = 2, padx = (10, 10), pady = 5, sticky = 'e')
    ENTRY_OF_HIGH_POWER_LIMIT = Entry(FRAME_OF_POWER_CONTROLS, font = (10), width = 15)
    ENTRY_OF_HIGH_POWER_LIMIT.grid(row = 0, column = 3, padx = (10, 10), pady = 10, ipady = 3, sticky = "w")

    # Increase Power Limit entry
    LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC = Label(FRAME_OF_POWER_CONTROLS, text = 'Increase Limit by(W) :', bg = "#575757", fg = 'white')
    LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row = 1, column = 0, padx = (10, 10), pady = 5, sticky = 'e')
    ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC = Entry(FRAME_OF_POWER_CONTROLS, font = (10), width = 15)
    ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row = 1, column = 1, padx = (10, 10), pady = 10, ipady = 3, sticky = "w")

    # Max Power Limit entry
    LABEL_OF_MAXIMUM_POWER_LIMIT = Label(FRAME_OF_POWER_CONTROLS, text = 'Max Limit(W) :', bg = "#575757", fg = 'white')
    LABEL_OF_MAXIMUM_POWER_LIMIT.grid(row = 1, column = 2, padx = (10, 10), pady = 5, sticky = 'e')
    ENTRY_OF_MAXIMUM_POWER_LIMIT = Entry(FRAME_OF_POWER_CONTROLS, font = (10), width = 15)
    ENTRY_OF_MAXIMUM_POWER_LIMIT.grid(row = 1, column = 3, padx = (10, 10), pady = 10, ipady = 3, sticky = "w")

    ## Creating entry fileds for PID values of CTC...
    FRAME_OF_PID = LabelFrame(CTC_TAB, text = "PID", fg = "white", bg = "#575757")
    FRAME_OF_PID.grid(row = 5, column = 0, sticky = "nesw", padx = 120, pady = (20,10))

    # P value of CTC entry
    LABEL_OF_P_VALUE_OF_CTC = Label(FRAME_OF_PID, text = "P :", fg = "white", bg = "#575757")
    LABEL_OF_P_VALUE_OF_CTC.grid(row = 0, column = 0, sticky = "ew", padx = (20,20), pady = 20)
    ENTRY_OF_P_VALUE_OF_CTC = Entry(FRAME_OF_PID, font = (10), width = 10)
    ENTRY_OF_P_VALUE_OF_CTC.grid(row = 0, column = 1, pady = 0, padx = (0,50), ipady = 3, sticky = "ew")

    # I value of CTC entry
    LABEL_OF_I_VALUE_OF_CTC = Label(FRAME_OF_PID, text = "I :", fg = "white", bg = "#575757")
    LABEL_OF_I_VALUE_OF_CTC.grid(row = 0, column = 2, sticky = "we", padx = (20,20))
    ENTRY_OF_I_VALUE_OF_CTC = Entry(FRAME_OF_PID, font = (10), width = 10)
    ENTRY_OF_I_VALUE_OF_CTC.grid(row = 0, column = 3, padx = (0,50), pady = 0, ipady = 3, sticky = "ew")

    # D value of CTC entry
    LABEL_OF_D_VALUE_OF_CTC = Label(FRAME_OF_PID, text = "D :", fg = "white",bg = "#575757")
    LABEL_OF_D_VALUE_OF_CTC.grid(row = 0, column = 4, sticky = "we", padx = (20,20))
    ENTRY_OF_D_VALUE_OF_CTC = Entry(FRAME_OF_PID, font = (10), width = 10)
    ENTRY_OF_D_VALUE_OF_CTC.grid(row = 0, column = 5, pady = 0, ipady = 3, sticky = "ew")

    

    ## Creating entry fileds for Temperature controls of CTC...
    FRAME_OF_TEMPERATURE_CONTROLS = LabelFrame(CTC_TAB, text = 'Temperature Controls', fg = 'white', bg="#575757")
    FRAME_OF_TEMPERATURE_CONTROLS.grid(row=6, column=0, rowspan=2, pady=(20, 10), padx=60, sticky='nwes', ipadx = 10)

    # Start Temperature entry
    LABEL_OF_START_TEMPERATURE = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Start Temperature(K) :', bg = "#575757", fg = 'white')
    LABEL_OF_START_TEMPERATURE.grid(row = 0, column = 0, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_START_TEMPERATURE = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_START_TEMPERATURE.grid(row = 0, column = 1, pady = 10, ipady = 3, sticky = "ew")

    # Stop Temperature entry
    LABEL_OF_STOP_TEMPERATURE = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Stop Temperature(K) :', bg = "#575757", fg = 'white')
    LABEL_OF_STOP_TEMPERATURE.grid(row = 0,  column = 2, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_STOP_TEMPERATURE = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_STOP_TEMPERATURE.grid(row = 0, column = 3, pady = 10, ipady = 3, sticky = "ew")

    # Increasing interval of Temperature entry
    LABEL_OF_INCREASING_INTERVAL_OF_TEMPERATURE = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Increasing by(K) :', bg = "#575757", fg = 'white')
    LABEL_OF_INCREASING_INTERVAL_OF_TEMPERATURE.grid(row = 0, column = 4, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE.grid(row = 0, column = 5, pady = 10, ipady = 3, sticky = "ew")

    # Threshold entry
    LABEL_OF_THRESHOLD = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Threshold :', bg = "#575757", fg = 'white')
    LABEL_OF_THRESHOLD.grid(row = 1, column = 0, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_THRESHOLD = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_THRESHOLD.grid(row = 1, column = 1, pady = 10, ipady = 3, sticky = "ew")

    # Tolerance entry
    LABEL_OF_TOLERANCE = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Tolerance :', bg = "#575757", fg = 'white')
    LABEL_OF_TOLERANCE.grid(row = 1, column = 2, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_TOLERANCE = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_TOLERANCE.grid(row = 1, column = 3, pady = 10, ipady = 3, sticky = "ew")

    # Delay of CTC entry
    LABEL_OF_DELAY_OF_CTC = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Delay of CTC(s):', bg = "#575757", fg = 'white')
    LABEL_OF_DELAY_OF_CTC.grid(row = 1, column = 4, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_DELAY_OF_CTC = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_DELAY_OF_CTC.grid(row = 1, column = 5, pady = 10, ipady = 3, sticky = "ew")

    # Complete Cycle entry
    COMPLETE_CYCLE = IntVar()
    COMPLETE_CYCLE_CHECKBUTTON=tb.Checkbutton(CTC_TAB, text = "Complete Cycle",  variable = COMPLETE_CYCLE, bootstyle="primary-round-toggle")
    COMPLETE_CYCLE_CHECKBUTTON.grid(row = 8, column = 0, pady = (20,10),padx=50)

 # Title
    TITLE_LFRAME = LabelFrame(CURRENT_SOURCE_TAB, text="Title", fg="white")
    TITLE_LFRAME.grid(row=0, column=0, rowspan=1, sticky="nsew", padx=300, pady=(60, 35))

    ENTRY_OF_TITLE = Entry(TITLE_LFRAME, font=(10), width=20)
    ENTRY_OF_TITLE.pack(pady=(0, 5), padx=10, ipady=5)
 
 # Drive
    DRIVE_LFRAME = LabelFrame(CURRENT_SOURCE_TAB, text="Current Controls", fg="white")
    DRIVE_LFRAME.grid(row=1, column=0, rowspan=4, sticky="nsew", padx=300, pady=30)

    CURRENT_START_LFRAME = LabelFrame(DRIVE_LFRAME, text="Current Start Value (A)", fg="white")
    CURRENT_START_LFRAME.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_START_CURRENT = Entry(CURRENT_START_LFRAME, font=(10), width=20)
    ENTRY_OF_START_CURRENT.grid(row=0, column=0,  pady=10, padx=10, ipady=5,ipadx=20, sticky="w")
    
    CURRENT_STOP_LFRAME = LabelFrame(DRIVE_LFRAME, text="Current Stop Value (A)", fg="white")
    CURRENT_STOP_LFRAME.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_STOP_CURRENT = Entry(CURRENT_STOP_LFRAME, font=(10), width=20)
    ENTRY_OF_STOP_CURRENT.grid(row=0, column=0,  pady=10, padx=10, ipady=5,ipadx=20,sticky="w")
   
    INTERVALNO_LFRAME = LabelFrame(DRIVE_LFRAME, text="Count(Number of Current Intervals at a Temperature)", fg="white")
    INTERVALNO_LFRAME.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS = Entry(INTERVALNO_LFRAME, font=(10), width=20)
    ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS.grid(row=0, column=0, pady=10, padx=10, ipady=5,ipadx=20,sticky="w")
    

    INTERVAL_LFRAME = LabelFrame(DRIVE_LFRAME, text="Step (Increase Current Interval at a Temperature)(A)", fg="white")
    INTERVAL_LFRAME.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT = Entry(INTERVAL_LFRAME, font=(10), width=20)
    ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT.grid(row=0, column=0,  pady=10, padx=10, ipady=5,ipadx=20,sticky="w")
    
    DELAY_LFRAME = LabelFrame(DRIVE_LFRAME, text="Delay (Pulse Width)", fg="white")
    DELAY_LFRAME.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_DELAY_OF_CURRENT_SOURCE = Entry(DELAY_LFRAME, font=(10), width=20)
    ENTRY_OF_DELAY_OF_CURRENT_SOURCE.grid(row=0, column=0,  pady=10, padx=10,ipady=5,ipadx=20,sticky="w")

    # Temperature Tab
    TERMPERATURE_LFRAME = LabelFrame(TEMPERATURE_TAB, text="Temperature and Time Controls", fg="white")
    TERMPERATURE_LFRAME.grid(row=0, column=0, rowspan=3,sticky="nsew", padx=(180,60), pady=150)

    SELECT_TEMP_LFRAME = LabelFrame(TERMPERATURE_LFRAME, text="Temperature(s)(in K)", fg="white")
    SELECT_TEMP_LFRAME.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")

    TEMPERATURES_ENTRY = Text(SELECT_TEMP_LFRAME, font=(10), width=20, height=1)
    TEMPERATURES_ENTRY.grid(row=0, column=0, pady=10, padx=10, ipady=5)
    
    TEMPERATURES_ENTRY.bind("<KeyRelease>", UPDATE_COMBOBOX) 
   

    MEASURING_TIME_LFRAME = LabelFrame(TERMPERATURE_LFRAME, text="Total Time( in s)", fg="white")
    MEASURING_TIME_LFRAME.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")

    MEASURING_TIME_ENTRY = Entry(MEASURING_TIME_LFRAME, font=(10), width=20)
    MEASURING_TIME_ENTRY.grid(row=0, column=0, pady=10, padx=10, ipady=5)
    

    NUMBER_OF_PULSES_PER_SECOND_LFRAME = LabelFrame(TERMPERATURE_LFRAME, text="Time Interval(in s)", fg="white")
    NUMBER_OF_PULSES_PER_SECOND_LFRAME.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

    NUMBER_OF_PULSES_PER_SECOND_ENTRY = Entry(NUMBER_OF_PULSES_PER_SECOND_LFRAME, font=(10), width=20)
    NUMBER_OF_PULSES_PER_SECOND_ENTRY.grid(row=0, column=0, rowspan=3, pady=10, padx=10, ipady=5)
    
     #CURRENT_CONTROLS
    CURRENT_CONTROLS_LFRAME = LabelFrame(TEMPERATURE_TAB, text="Current Controls", fg="white")
    CURRENT_CONTROLS_LFRAME.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(60,180), pady=100)

    HIGH_LFRAME = LabelFrame(CURRENT_CONTROLS_LFRAME, text="High current of pulse(A)", fg="white")
    HIGH_LFRAME.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_HIGH_PULSE = Entry(HIGH_LFRAME, font=(10), width=20)
    ENTRY_OF_HIGH_PULSE.grid(row=0, column=0,  pady=10, padx=10, ipady=5,ipadx=20, sticky="w")
    
    LOW_LFRAME = LabelFrame(CURRENT_CONTROLS_LFRAME, text="Low current of pulse(A)", fg="white")
    LOW_LFRAME.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_LOW_PULSE = Entry(LOW_LFRAME, font=(10), width=20)
    ENTRY_OF_LOW_PULSE.grid(row=0, column=0,  pady=10, padx=10, ipady=5,ipadx=20,sticky="w")
   
    WIDTH_LFRAME = LabelFrame(CURRENT_CONTROLS_LFRAME, text="Width of the pulse(s)", fg="white")
    WIDTH_LFRAME.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_PULSE_WIDTH = Entry(WIDTH_LFRAME, font=(10), width=20)
    ENTRY_OF_PULSE_WIDTH.grid(row=0, column=0, pady=10, padx=10, ipady=5,ipadx=20,sticky="w")
    
    NUMBER_OF_PULSES_PER_SECOND_LFRAME = LabelFrame(CURRENT_CONTROLS_LFRAME, text="Pulse Interval(s)", fg="white")
    NUMBER_OF_PULSES_PER_SECOND_LFRAME.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="w")

    ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND = Entry(NUMBER_OF_PULSES_PER_SECOND_LFRAME, font=(10), width=20)
    ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND.grid(row=0, column=0, pady=10, padx=10, ipady=5,ipadx=20,sticky="w")
    


    # Setup the graph_tab...
    SET_R_vs_Temp_Graph(GRAPH_R_vs_Temp)
    SET_R_vs_Time_Graph(GRAPH_R_vs_Time_final)
    
            ### other ###
    # INTERFACE.protocol("WM_DELETE_WINDOW", CONFIRM_TO_QUIT)
    INTERFACE.wait_visibility()
    INTERFACE.update()
    
    root_width=INTERFACE.winfo_width()
    root_height=INTERFACE.winfo_height()
    INTERFACE.geometry(CENTER_THE_WIDGET(root_width,root_height))
    INTERFACE.minsize(root_width,root_height)
    
    # SETTINGS_WIDGET_TEMPERATURE_CONTROL()
    DISPLAY_REQUIREMENTS()
    DISPLAY_SELECTING_EXPERIMENTS_WIDGET()

    
    INTERFACE.mainloop()
