#### By Sai Pranay Deep, Aditi Wekhande, Devanshi Chhatbar, Saket Meshram, Jay Solanki.... ####

# Note :- We have used Ethernet cable for CTC device, GPIB cable for Nanovoltmeter, RS232 cable for AC/DC current source. The code may change if you use different cables... :)


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
from threading import Thread

# Required imports for maintaining the data
import csv, json
import numpy as np


# Required import to make the program sleep
import time


# Required import for Directories of files
from datetime import datetime
from os.path import exists
from os import mkdir

####-------------------------------------- Graph Plotting Part -------------------------------------------------####

# Array to store the lines...
ARRAY_OF_PLOTTING_LINES = [] 

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


# Function to setup the Graph in Graph tab...
def SET_GRAPH_IN_TAB(GRAPH_TAB):

    global FRAME_OF_GRAPH, LABEL_OF_GRAPH, FIGURE_OF_GRAPH, CANVAS_OF_GRAPH, GRAPH, ANNOTATION, TOOLBAR_OF_GRAPH, Y_COORDINATE_OF_LAST_ADDED_POINT, X_COORDINATE_OF_LAST_ADDED_POINT

    FRAME_OF_GRAPH = Frame(GRAPH_TAB) 

    LABEL_OF_GRAPH = tk.Label(FRAME_OF_GRAPH, text = "Resistance Vs. Temperature") # Adding label/title for the graph

    LABEL_OF_GRAPH.config(font=('Times', 32)) # Changing the default font style and size to Times and 32

    FIGURE_OF_GRAPH = Figure() # Created a figure to add graph

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
    CANVAS_OF_GRAPH.get_tk_widget().pack(fill="both", expand=True)
    FRAME_OF_GRAPH.pack(fill="both", expand=True)


####---------------------------------------- Experiment Part ---------------------------------------------------####

# Function to check whether all the instruments are connected or not...
def CONNECT_INSTRUMENTS(): 
    global NANOVOLTMETER, CURRENT_SOURCE, CTC, MAX_RETRY

    MAX_RETRY = 10
    number_of_connected_devices = 0
    retry_number = 0

    # Connecting Nanovoltmeter
    while True:
        try:
            rm = pyvisa.ResourceManager()
            NANOVOLTMETER = rm.open_resource('GPIB0::2::INSTR')
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showinfo("Alert","NANOVOLTMETER is not connected... Check its connections!!")
                retry_number = 0
                break
            retry_number += 1

    # Connecting Current source
    while True:
        try:
            CURRENT_SOURCE = serial.Serial('COM1', baudrate=9600,timeout=10)
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showinfo("Alert","CURRENT SOURCE is not connected... Check its connections!")
                retry_number = 0
                break
            retry_number += 1

    # connecting CTC
    while True:
        try:
            CTC = telnetlib.Telnet("192.168.0.2",23,10)
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showinfo("Alert","CTC is not connected... Check its connections!")
                retry_number = 0
                break
            retry_number += 1
    

    # Returning 1 if all three devices are connected, otherwise -1
    if number_of_connected_devices == 3: 
        return 1 
    else: 
        return -1


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

    print("*************************************************************************")
    print("===> Achieving", required_temperature, "K...")

    SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.HiLmt" '+str(HIGH_POWER_LIMIT_OF_CTC)) # Setting High Limit of CTC to HIGH_POWER_LIMIT_OF_CTC...

    SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.PID.Setpoint" '+str(required_temperature)) # Setting the setpoint of CTC to required_temperature...


    retry_number = 0
    temperature_before_stabilizing = GET_PRESENT_TEMPERATURE_OF_CTC()

    lower_bound = required_temperature - THRESHOLD
    upper_bound = required_temperature + THRESHOLD

    while(True):

        time.sleep(3)
        present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

        if lower_bound <= present_temperature <= upper_bound :
            print(required_temperature, "K is achieved but not stabilized...")
            break

        else:
            print("Current Temperature is", present_temperature, "... Waiting to achieve required temperature ", required_temperature, "K...")
            retry_number += 1

        if retry_number == MAX_RETRY : # Increasing the high limit of power if possible...

            if HIGH_POWER_LIMIT_OF_CTC + INCREASE_POWER_LIMIT_OF_CTC <= MAXIMUM_POWER_LIMIT_OF_CTC :

                if present_temperature <= temperature_before_stabilizing :

                    HIGH_POWER_LIMIT_OF_CTC += INCREASE_POWER_LIMIT_OF_CTC
                    SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.HiLmt" ' + str(HIGH_POWER_LIMIT_OF_CTC))

                    print(required_temperature," K is not achieving by current high power limit of CTC...")
                    print("So, Increased high power limit of CTC by "+str(INCREASE_POWER_LIMIT_OF_CTC)," W...")
                    print("New High power limit of CTC is ",HIGH_POWER_LIMIT_OF_CTC,"...")

                    # We are starting again by increasing high power limit of ctc... So...
                    retry_number = 0 
                    temperature_before_stabilizing = present_temperature

            else:
                messagebox.showinfo("Alert","Cannot Achieve all the temperatures by given Maximum limit of Power!!")
                raise Exception("Cannot Achieve all the temperatures by given Maximum limit of Power")
            
    print("______________________________________________________________________")
    print("===> Stabilizing at", required_temperature, "K...")

    while(True):

        minimum_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()
        maximum_temperature = minimum_temperature
        retry_number = 0

        while(retry_number < MAX_RETRY):

            present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

            print("Current temperature =", present_temperature, " K")

            if present_temperature > maximum_temperature: maximum_temperature = present_temperature
            if present_temperature < minimum_temperature: minimum_temperature = present_temperature
            
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

    reading_number = 0
    present_current = START_CURRENT

    resistance_readings = [] # Array to store resistance values at five different DC Currents...

    while(reading_number < NUMBER_OF_CURRENT_INTERVALS):

        # Sending command to set the output current to present_current...
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR " + str(present_current))

        time.sleep(3) # Waiting some time...

        # Get the voltage reading...
        positive_cycle_voltage = GET_PRESENT_VOLTAGE_READING()

        print("Current :",present_current, ", Voltage :",positive_cycle_voltage, ", Resistance :",abs(positive_cycle_voltage) / present_current, "...")

        resistance_readings.append(abs(positive_cycle_voltage) / present_current)

        # Sending command to set the output current to -present_current...
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR -" + str(present_current))

        time.sleep(3) # Waiting some time...

        # Get the voltage reading...
        negative_cycle_voltage = GET_PRESENT_VOLTAGE_READING()
        resistance_readings.append(abs(negative_cycle_voltage) / present_current)

        print("Current :",present_current, ", Voltage :",positive_cycle_voltage, ", Resistance :",(abs(positive_cycle_voltage) / present_current), "...")

        present_current += INCREASING_INTERVAL_OF_CURRENT
        reading_number += 1
    
    SEND_COMMAND_TO_CURRENT_SOURCE("OUTP OFF") # Switching Current_Source output OFF
    
    return sum(resistance_readings) / len(resistance_readings)


# Function to write the temperature and resistance values into csv file
def WRITE_DATA_TO_CSV(temperature, resistance):

    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
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
        
        print("Resistance of the sample is", present_resistance, "Ohm, at temperature", present_temperature, "K...")

        # Writing the present temperature and resistance into csv file...
        WRITE_DATA_TO_CSV(present_temperature, present_resistance)

        # Plotting the present point in the graph...
        ADD_POINT_TO_GRAPH(present_temperature, present_resistance)

        # Increase or decrease the temperature according to the direction...
        present_temperature += INCREASING_INTERVAL_OF_TEMPERATURE * direction 

    # Switching CTC output OFF
    SEND_COMMAND_TO_CTC("outputEnable off")


# Function to check whether the input values given by the user are in correct data types and are in correct range or not.. If they are correct the value will be set to the devices..
def CHECK_AND_SET_ALL_VALUES(): 

    global INPUT_CHANNEL_OF_CTC, TOLERANCE, OUTPUT_CHANNEL_OF_CTC, HIGH_POWER_LIMIT_OF_CTC, LOW_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC, THRESHOLD, START_CURRENT, NUMBER_OF_CURRENT_INTERVALS, INCREASING_INTERVAL_OF_CURRENT, START_TEMPERATURE, END_TEMPERATURE, DELAY_OF_CTC, INCREASING_INTERVAL_OF_TEMPERATURE, COMPLETE_CYCLE, CSV_FILE_NAME, P_VALUE_OF_CTC, I_VALUE_OF_CTC, D_VALUE_OF_CTC


    # Assigning the parameters of CTC given by user to the variables and Setting those to CTC if they are in correct format...

    INPUT_CHANNEL_OF_CTC = ENTRY_OF_INPUT_CHANNEL.get().replace(" ", "") # Converting In 1, In 2,... as In, In,..., Because CTC takes the input channel whithout spaces...

    OUTPUT_CHANNEL_OF_CTC = ENTRY_OF_OUTPUT_CHANNEL.get().replace(" ", "") # Converting Out 1, Out 2,... as Out1, Out2,..., Because CTC takes the output channel whithout spaces...

    try:
        HIGH_POWER_LIMIT_OF_CTC = float(ENTRY_OF_HIGH_POWER_LIMIT.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.HiLmt" ' + str(HIGH_POWER_LIMIT_OF_CTC))
    except:
        messagebox.showinfo("Alert","Invalid Input for: High Limit !")
        return -1

    try:
        LOW_POWER_LIMIT_OF_CTC = float(ENTRY_OF_LOW_POWER_LIMIT.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.LowLmt" ' + str(LOW_POWER_LIMIT_OF_CTC))
    except:
        messagebox.showinfo("Alert","Invalid Input for: Low Limit !")
        return -1

    try:
        INCREASE_POWER_LIMIT_OF_CTC = float(ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Increase By !")
        return -1
    
    try:
        MAXIMUM_POWER_LIMIT_OF_CTC = float(ENTRY_OF_MAXIMUM_POWER_LIMIT.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Max Limit !")
        return -1

    try:
        P_VALUE_OF_CTC = float(ENTRY_OF_P_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.P" ' + str(P_VALUE_OF_CTC))
    except:
        messagebox.showinfo("Alert","Invalid Input for P !")
        return -1
    
    try:
        I_VALUE_OF_CTC = float(ENTRY_OF_I_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.I" ' + str(I_VALUE_OF_CTC))
    except:
        messagebox.showinfo("Alert","Invalid Input for I !")
        return -1
    
    try:
        D_VALUE_OF_CTC = float(ENTRY_OF_D_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.D" ' + str(D_VALUE_OF_CTC))
    except:
        messagebox.showinfo("Alert","Invalid Input for D !")
        return -1
    
    try:
        START_TEMPERATURE = float(ENTRY_OF_START_TEMPERATURE.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Start Temp!")
        return -1
    
    try:
        END_TEMPERATURE = float(ENTRY_OF_STOP_TEMPERATURE.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Stop Temp!")
        return -1
    
    try:
        INCREASING_INTERVAL_OF_TEMPERATURE = float(ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Interval Temp!")
        return -1
    
    try:
        THRESHOLD = float(ENTRY_OF_THRESHOLD.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Threshold!")
        return -1
    
    try:
        TOLERANCE = float(ENTRY_OF_TOLERANCE.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Tolerance!")
        return -1
    
    try:
        DELAY_OF_CTC = float(ENTRY_OF_DELAY_OF_CTC.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Avg Delay!")
        return -1
    
    COMPLETE_CYCLE = int(ENTRY_OF_COMPLETE_CYCLE.get()) # No need to check it as it is a checkbox...



    # Assigning the parameters of Current Source given by user to the variables if they are in correct format...

    try:
        START_CURRENT = float(ENTRY_OF_START_CURRENT.get())
        if not START_CURRENT < 1:
            messagebox.showinfo("Alert! Enter the Current value less than 1 Ampere !")
            return -1
    except:
        messagebox.showinfo("Alert","Invalid Input for Start Current Value!")
        return -1

    try:
        NUMBER_OF_CURRENT_INTERVALS = int(ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Number of Current Intervals at a Temperature!")
        return -1
    
    try:
        INCREASING_INTERVAL_OF_CURRENT = float(ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT.get())
    except:
        messagebox.showinfo("Alert","Invalid Input for Increase Current Interval at a Temperature!")
        return -1


    # The title should not consists the following invalid characters...
    invalid_characters=['\\','/',':','*','?','"','<','>','|']
    CSV_FILE_NAME = ENTRY_OF_CSV_FILE_NAME.get()

    if CSV_FILE_NAME == "" : messagebox.showinfo("Alert",'No input is given for Title!')
    for Character in invalid_characters:
        if Character in CSV_FILE_NAME:
            CSV_FILE_NAME = None
            messagebox.showinfo("Alert",'Invalid Input for Title !\nCannot contain \\ / : * ? " < > |')
            return -1

    return 1 


# Function to start the Experiment...
def START_EXPERIMENT():

    # Getting resistances from starting temperature to end temperature(forward cycle)... The function is defined above...
    GET_RESISTANCE_AT_ALL_TEMPERATURES(START_TEMPERATURE, END_TEMPERATURE)
    
    if COMPLETE_CYCLE : GET_RESISTANCE_AT_ALL_TEMPERATURES(END_TEMPERATURE, START_TEMPERATURE)


# Function to trigger the Experiment... 
def TRIGGER():

    if(CHECK_AND_SET_ALL_VALUES() == -1): # Checking and Setting all values...
        return

    CONTROL_PANEL.select(2) # Displaying Graph tab when experiment is started...

    print("Checking Devices....")

    if CONNECT_INSTRUMENTS() == 1:
        Thread(target = START_EXPERIMENT).start() # Starting the experiment and threading to make GUI accessable even after the experiment is start... 
        
    else:
        messagebox.showinfo("Alert","Could not connect... CHECK ALL CONNECTIONS AND WIRES AND RETRY")
    

####---------------------------------------- Interface Part -------------------------------------------------####

# Function to Confirm the user before quiting Interface...
def CONFIRM_TO_QUIT(): 
   if messagebox.askokcancel("Quit", "Are you Sure!! Do you want to quit?"):
        # export_config()
        INTERFACE.destroy()


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
def CLOSE_WIDGET(widget, callback=None): 
    widget.destroy()
    INTERFACE.update()
    if(callback != None):
        callback()


# Function to open filedialog to select the directory...
def OPEN_FILEDIALOG(out_dir_label): 
    directory = filedialog.askdirectory()
    if directory:
        SETTINGS["output_dir"] = directory
        WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE()
        out_dir_label.config(text = directory)


# Function to Create and Open Settings Widget and saving the changes if any are done in this widget...
def OPEN_SETTINGS_WIDGET(): 

    # Creating Settings Widget...
    SETTINGS_WIDGET = Toplevel(INTERFACE)
    SETTINGS_WIDGET.config(bg = "#575757")
    SETTINGS_WIDGET.title("Settings")
    SETTINGS_WIDGET.geometry(CENTER_THE_WIDGET(500, 270))
    SETTINGS_WIDGET.resizable(False,False)
    SETTINGS_WIDGET.grid_columnconfigure(0,weight=1)
    SETTINGS_WIDGET.grid_columnconfigure(1,weight=1)

    # Creating Combobox for selecting GPIB Cabel connected to Nanovoltmeter...
    Label(SETTINGS_WIDGET, text = "Nanovoltmeter", fg = "white", bg = "#575757").grid(row = 0,column = 0, rowspan = 2, sticky = "e", padx = (0,10), pady = 10)
    
    cabels_available = StringVar(value = SETTINGS["device_name"]) # Assigning the variable with the cabel which is in settings (Simply setting default)

    device_options = ttk.Combobox(SETTINGS_WIDGET, width = 27, textvariable = cabels_available, state = "readonly")
    device_options.bind('<<ComboboxSelected>>', lambda x: SET_SETTINGS("device_name", device_options.get()))
    device_options.grid(row = 0, column = 1, sticky = "w", pady = 10)


    # Creating an entry field to enter the address of the CTC device...
    Label(SETTINGS_WIDGET,text = "CTC Address:", fg = "white", bg = "#575757").grid(row = 2, column = 0, sticky = "e", padx = (0,10), pady = 10)

    ctc_address = StringVar(value = SETTINGS["ctc_address"]) # Assigning the variable with the address which is in settings (Simply setting default)

    ctc_address_entry = Entry(SETTINGS_WIDGET, font = (10), width = 15, textvariable = ctc_address)
    ctc_address_entry.grid(row = 2, column = 1, pady = 0, sticky = "w")
    ctc_address_entry.bind("<KeyRelease>", lambda x: SET_SETTINGS("ctc_address", ctc_address.get())) #updates ctc_adress on any key release event


    # Creating an entry field to enter the CTC Telnet...
    Label(SETTINGS_WIDGET, text = "CTC Telnet:", fg = "white", bg = "#575757").grid(row = 3, column = 0, sticky = "e", padx = (0,10), pady = 10)

    ctc_telnet_var = StringVar(value = SETTINGS["ctc_telnet"])

    ctc_telnet_entry = Entry(SETTINGS_WIDGET, font = (10), width = 15, textvariable = ctc_telnet_var)
    ctc_telnet_entry.grid(row = 3, column = 1, pady = 0, sticky = "w")
    ctc_telnet_entry.bind("<KeyRelease>",lambda x: SET_SETTINGS("ctc_telnet", ctc_telnet_var.get()))
    

    # Creating an entry field to enter the port of RS232 cabel connected to AC/DC Current Source...
    Label(SETTINGS_WIDGET, text = "RS232:", fg = "white", bg = "#575757").grid(row = 4, column = 0, sticky = "e", padx = (0,10), pady = 10)

    rs232_var = StringVar(value = SETTINGS["rs232"])

    rs232_entry = Entry(SETTINGS_WIDGET, font = (10), width = 15, textvariable = rs232_var)
    rs232_entry.grid(row = 4, column = 1, pady = 0, sticky = "w")
    rs232_entry.bind("<KeyRelease>", lambda x: SET_SETTINGS("rs232", rs232_var.get()))

    # Creating an entry field to enter the Max_retry number...
    Label(SETTINGS_WIDGET, text = "Max_Retry:", fg = "white", bg = "#575757").grid(row = 5, column = 0, sticky = "e", padx = (0,10), pady = 10)

    max_retry_var = StringVar(value = SETTINGS["max_retry"])

    max_retry_entry = Entry(SETTINGS_WIDGET, font = (10), width = 10, textvariable = max_retry_var)
    max_retry_entry.grid(row = 5, column = 1, pady = 0, sticky = "w")
    max_retry_entry.bind("<KeyRelease>", lambda x: SET_SETTINGS("max_retry", max_retry_var.get()))

    # Creating a dialougebox for selecting the directory...
    Label(SETTINGS_WIDGET, text = "Output Directory:", fg = "white", bg = "#575757").grid(row = 6, column = 0, sticky = "e", padx = (0,10), pady = 10)
    out_dir_label = Label(SETTINGS_WIDGET,text = SETTINGS["output_dir"], anchor = "w", width = 25, fg = "white", bg = "#575757")
    out_dir_label.grid(row = 6, column = 1, sticky = "w", padx = (0,10), pady = 10)
    Button(SETTINGS_WIDGET, text = "Select Folder", command = lambda: OPEN_FILEDIALOG(out_dir_label)).grid(row = 6, column = 1, padx = (150,0), pady = 10)

    SETTINGS_WIDGET.protocol("WM_DELETE_WINDOW", lambda : CLOSE_WIDGET(SETTINGS_WIDGET))
    SETTINGS_WIDGET.grab_set()
    SETTINGS_WIDGET.mainloop()


# Function to display the info of devices...
def SHOW_INFO_OF_DEVICES(): 

    if CONNECT_INSTRUMENTS() :
        info_of_nanovoltmeter = str(NANOVOLTMETER.query("*IDN?"))
        info_of_current_source = str(SEND_COMMAND_TO_CURRENT_SOURCE("*IDN?"))
        info_of_ctc = str(SEND_COMMAND_TO_CTC("description?"))

        info_of_devices = "Nanovoltmeter :" + info_of_nanovoltmeter + "\nCurrent Source :" + info_of_current_source + "\nCTC Device: " + info_of_ctc

        messagebox.showinfo("Device Info", info_of_devices)
        

# Default Settings...
SETTINGS = {"device_name":"GPIB0::6::INSTR",
            "output_dir":"./",
            "ctc_address":"192.168.0.2",
            "ctc_telnet":"23",
            "rs232":"COM 1",
            "max_retry":"10"
            }


# Function to change the settings...
def SET_SETTINGS(key,val): 
    SETTINGS[key] = val
    WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE()


if __name__=="__main__":

    ## Creating a Tkinter Interface ##
    INTERFACE = Tk() # Made a root Interface
    INTERFACE.wm_title("TD-Controller") # Set title to the interface widget
    INTERFACE.geometry("850x600") # Set Geometry of the interface widget
    INTERFACE.grid_columnconfigure(0, weight=1) 
    INTERFACE.grid_rowconfigure(0, weight=1)


    ## Creating a Sidebar and adding Trigger, Settings, Info, Sync Set, Sync Get buttons ## 
    SIDE_BAR = Frame(INTERFACE, bg="#878787")
    SIDE_BAR.grid(row=0, column=1, rowspan=2, sticky="nswe")

    SETTINGS_BUTTON = Button(SIDE_BAR, text = "Settings", height = 2, command = OPEN_SETTINGS_WIDGET)
    SETTINGS_BUTTON.pack(side="bottom",pady=(5,0),fill='x',padx=2)

    INFO_BUTTON = Button(SIDE_BAR, text = "Info", height = 2, command = SHOW_INFO_OF_DEVICES)
    INFO_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)

    SYNC_SET_BUTTON = Button(SIDE_BAR, text = "Sync Set", height= 2)
    SYNC_SET_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)

    SYNC_GET_BUTTON= Button(SIDE_BAR, text = "Sync Get", height = 2)
    SYNC_GET_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)

    TRIGGER_BUTTON = Button(SIDE_BAR, text = "Trigger", height = 2, command = TRIGGER)
    TRIGGER_BUTTON.pack(side = "bottom", pady = (5,0), fill = 'x', padx = 2)


    ## Creating Control Panel and adding CTC tab, Current Source tab and Graph tab ##
    CONTROL_PANEL = ttk.Notebook(INTERFACE)

    CTC_TAB = Frame(CONTROL_PANEL,bg="#575757") 
    CURRENT_SOURCE_TAB = Frame(CONTROL_PANEL,bg="#575757") 
    GRAPH_TAB = Frame(CONTROL_PANEL) 

    CONTROL_PANEL.add(CTC_TAB, text = ' CTC\n Setup ')
    CONTROL_PANEL.add(CURRENT_SOURCE_TAB , text = ' Current Source\n      Setup ')
    CONTROL_PANEL.add(GRAPH_TAB, text = ' Graph\n Setup ')
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
    LABEL_OF_LOW_POWER_LIMIT = Label(FRAME_OF_POWER_CONTROLS, text = 'Low Limit :', bg = "#575757", fg = 'white')
    LABEL_OF_LOW_POWER_LIMIT.grid(row = 0, column = 0, padx = (10, 10), pady = 5, sticky = 'e')
    ENTRY_OF_LOW_POWER_LIMIT = Entry(FRAME_OF_POWER_CONTROLS, font = (10), width = 15)
    ENTRY_OF_LOW_POWER_LIMIT.grid(row = 0, column = 1, padx = (10, 10), pady = 10, ipady = 3, sticky = "w")

    # High Power Limit entry
    LABEL_OF_HIGH_POWER_LIMIT = Label(FRAME_OF_POWER_CONTROLS, text = 'High Limit :', bg = "#575757", fg = 'white')
    LABEL_OF_HIGH_POWER_LIMIT.grid(row = 0, column = 2, padx = (10, 10), pady = 5, sticky = 'e')
    ENTRY_OF_HIGH_POWER_LIMIT = Entry(FRAME_OF_POWER_CONTROLS, font = (10), width = 15)
    ENTRY_OF_HIGH_POWER_LIMIT.grid(row = 0, column = 3, padx = (10, 10), pady = 10, ipady = 3, sticky = "w")

    # Increase Power Limit entry
    LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC = Label(FRAME_OF_POWER_CONTROLS, text = 'Increase Limit by :', bg = "#575757", fg = 'white')
    LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row = 1, column = 0, padx = (10, 10), pady = 5, sticky = 'e')
    ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC = Entry(FRAME_OF_POWER_CONTROLS, font = (10), width = 15)
    ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row = 1, column = 1, padx = (10, 10), pady = 10, ipady = 3, sticky = "w")

    # Max Power Limit entry
    LABEL_OF_MAXIMUM_POWER_LIMIT = Label(FRAME_OF_POWER_CONTROLS, text = 'Max Limit :', bg = "#575757", fg = 'white')
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
    LABEL_OF_START_TEMPERATURE = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Start Temperature :', bg = "#575757", fg = 'white')
    LABEL_OF_START_TEMPERATURE.grid(row = 0, column = 0, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_START_TEMPERATURE = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_START_TEMPERATURE.grid(row = 0, column = 1, pady = 10, ipady = 3, sticky = "ew")

    # Stop Temperature entry
    LABEL_OF_STOP_TEMPERATURE = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Stop Temperature :', bg = "#575757", fg = 'white')
    LABEL_OF_STOP_TEMPERATURE.grid(row = 0,  column = 2, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_STOP_TEMPERATURE = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_STOP_TEMPERATURE.grid(row = 0, column = 3, pady = 10, ipady = 3, sticky = "ew")

    # Increasing interval of Temperature entry
    LABEL_OF_INCREASING_INTERVAL_OF_TEMPERATURE = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Increasing by :', bg = "#575757", fg = 'white')
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
    LABEL_OF_DELAY_OF_CTC = Label(FRAME_OF_TEMPERATURE_CONTROLS, text = 'Delay of CTC :', bg = "#575757", fg = 'white')
    LABEL_OF_DELAY_OF_CTC.grid(row = 1, column = 4, padx = 30, pady = 5, sticky = 'ew')
    ENTRY_OF_DELAY_OF_CTC = Entry(FRAME_OF_TEMPERATURE_CONTROLS, font = (10), width = 7)
    ENTRY_OF_DELAY_OF_CTC.grid(row = 1, column = 5, pady = 10, ipady = 3, sticky = "ew")

    # Complete Cycle entry
    ENTRY_OF_COMPLETE_CYCLE = IntVar()
    Checkbutton(CTC_TAB, text = "Complete Cycle", fg = "white", bg = "#575757", highlightthickness = 0, variable = ENTRY_OF_COMPLETE_CYCLE, activebackground = "#575757", activeforeground = 'white', selectcolor = "black").grid(row = 8, column = 0, pady = 20, sticky = "ew")

    # CSV File Name entry
    FRAME_OF_CSV_FILE_NAME = LabelFrame(CURRENT_SOURCE_TAB, text = "Title", fg = "white", bg = "#575757")
    FRAME_OF_CSV_FILE_NAME.grid(row = 0, column = 0, rowspan = 1, sticky = "nsew", padx = 250, pady = (40, 25))
    ENTRY_OF_CSV_FILE_NAME = Entry(FRAME_OF_CSV_FILE_NAME, font = (10), width = 20)
    ENTRY_OF_CSV_FILE_NAME.pack(pady = (0,5), padx = 10, ipady = 5)

    ## Creating entry fileds for Current controls...
    FRAME_OF_CURRENT_CONTROLS = LabelFrame(CURRENT_SOURCE_TAB, text = "Current Controls", fg = "white", bg= "#575757")
    FRAME_OF_CURRENT_CONTROLS.grid(row=1, column=0, sticky="nsew", padx=250, pady=25)

    # Start Current entry
    LABEL_OF_START_CURRENT = Label(FRAME_OF_CURRENT_CONTROLS, text = "Start Current:", fg = "white", bg= "#575757")
    LABEL_OF_START_CURRENT.grid(row=0, column=0, padx=(10, 5), pady=(15, 10), sticky="w")  
    ENTRY_OF_START_CURRENT = Entry(FRAME_OF_CURRENT_CONTROLS, font=(None, 10), width=20)
    ENTRY_OF_START_CURRENT.grid(row=0, column=1, padx=(0, 10), pady=(10, 10), ipady=5, sticky="w")  

    # Number of current intervals entry
    LABEL_OF_NUMBER_OF_CURRENT_INTERVALS = Label(FRAME_OF_CURRENT_CONTROLS, text = "No. of Current Intervals:", fg = "white", bg= "#575757")
    LABEL_OF_NUMBER_OF_CURRENT_INTERVALS.grid(row=1, column=0, padx=(10, 5), pady=(10, 10), sticky="w")  
    ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS = Entry(FRAME_OF_CURRENT_CONTROLS, font=(None, 10), width=20)
    ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS.grid(row=1, column=1, padx=(0, 10), pady=(10, 10), ipady=5, sticky="w")  

    # Increasing interval of current entry
    LABEL_OF_INCREASING_INTERVAL_OF_CURRENT = Label(FRAME_OF_CURRENT_CONTROLS, text = "Increase by:", fg = "white", bg= "#575757")
    LABEL_OF_INCREASING_INTERVAL_OF_CURRENT.grid(row=2, column=0, padx=(10, 5), pady=(10, 10), sticky="w")  
    ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT = Entry(FRAME_OF_CURRENT_CONTROLS, font=(None, 10), width=20)
    ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT.grid(row=2, column=1, padx=(0, 10), pady=(10, 10), ipady=5, sticky="w")  

    # Setup the graph_tab...
    SET_GRAPH_IN_TAB(GRAPH_TAB)

    INTERFACE.protocol("WM_DELETE_WINDOW", CONFIRM_TO_QUIT)
    INTERFACE.wait_visibility()
    INTERFACE.update()
    

    INTERFACE.geometry(CENTER_THE_WIDGET(INTERFACE.winfo_width(), INTERFACE.winfo_height()))
    INTERFACE.minsize(INTERFACE.winfo_width(), INTERFACE.winfo_height())

    INTERFACE.mainloop()
