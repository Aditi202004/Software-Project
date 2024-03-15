
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

    # Connecting Nanovoltmeter with Pyvisa
    rm = pyvisa.ResourceManager()
    NANOVOLTMETER = rm.open_resource('GPIB0::2::INSTR')

    # Connecting AC/DC Current Source with PySerial
    CURRENT_SOURCE = serial.Serial('COM1', baudrate=9600,timeout=10)

    # Connecting CTC with Telnet
    CTC = telnetlib.Telnet("192.168.0.2",23,10)


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

    while(reading < 5):

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

        # Plotting the point in the graph...
        ADD_POINT_TO_GRAPH(present_temperature, present_resistance)

        present_temperature += INCREASING_INTERVAL_OF_TEMPERATURE * direction


    SEND_COMMAND_TO_CTC("outputEnable off")


# Fuction to start the experiment...
def TRIGGER():
    global MAX_RETRY, INPUT_CHANNEL_OF_CTC, TOLERANCE, OUTPUT_CHANNEL_OF_CTC, HIGH_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC, THRESHOLD, START_CURRENT, INCREASING_INTERVAL_OF_CURRENT, START_TEMPERATURE, END_TEMPERATURE, DELAY_OF_CTC, INCREASING_INTERVAL_OF_TEMPERATURE, COMPLETE_CYCLE, CSV_FILE

    # Connecting CTC, Nanovoltmeter and AC/DC Current Source... The function is defined above...
    CONNECT_INSTRUMENTS()

    # Getting resistances from starting temperature to end temperature(forward cycle)... The function is defined above...
    GET_RESISTANCE_AT_ALL_TEMPERATURES(START_TEMPERATURE, END_TEMPERATURE)
    
    if COMPLETE_CYCLE : GET_RESISTANCE_AT_ALL_TEMPERATURES(END_TEMPERATURE, START_TEMPERATURE)


#%%


#-------------------------------------------- Interface Part ----------------------------------------------------#




