import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("dark-blue")


INTERFACE = ctk.CTk()
INTERFACE.geometry("700x600")
INTERFACE.title("Resistance Plotter")
INTERFACE.columnconfigure(0, weight=6, uniform='a')
INTERFACE.columnconfigure(1, weight=1, uniform='a')
INTERFACE.rowconfigure((0,1), weight=1, uniform='a')


SIDE_BAR = ctk.CTkFrame(INTERFACE, width=75)
SIDE_BAR.grid(row=1, column=1, padx=(5,20), pady=10, sticky="nsew")
SIDE_BAR.rowconfigure((0,1,2,3,4), weight=1, uniform='a')
SIDE_BAR.columnconfigure(0, weight=1)

TRIGGER_BUTTON = ctk.CTkButton(SIDE_BAR, text="Trigger", width=0)
SYNC_GET_BUTTON = ctk.CTkButton(SIDE_BAR, text="Sync\nGet", width=0)
SYNC_SET_BUTTON = ctk.CTkButton(SIDE_BAR, text="Sync\nSet", width=0)
INFO_BUTTON = ctk.CTkButton(SIDE_BAR, text="Info", width=0)
SETTINGS_BUTTON = ctk.CTkButton(SIDE_BAR, text="Settings", width=0)

TRIGGER_BUTTON.grid(row=0, column=0, sticky="nsew",pady=2.5)
SYNC_GET_BUTTON.grid(row=1, column=0, sticky="nsew",pady=2.5)
SYNC_SET_BUTTON.grid(row=2, column=0, sticky="nsew",pady=2.5)
INFO_BUTTON.grid(row=3, column=0, sticky="nsew",pady=2.5)
SETTINGS_BUTTON.grid(row=4, column=0, sticky="nsew",pady=2.5)

CONTROL_PANEL = ctk.CTkTabview(INTERFACE)
CONTROL_PANEL.grid(row=0, column=0,rowspan=2, padx=(20,5), pady=10, sticky="nsew")

CTC_TAB = CONTROL_PANEL.add("CTC\nSetup")
CURRENT_SOURCE_TAB = CONTROL_PANEL.add("Resistance Vs Temp\nSetup")
GRAPH_TAB = CONTROL_PANEL.add("Graph\nSetup")

FRAME_OF_TITLE = ctk.CTkFrame(CTC_TAB, height=10, fg_color="#3D3C3A")
FRAME_OF_TITLE.pack(padx=5, pady=5, fill="both", expand=True)
FRAME_OF_TITLE.columnconfigure((0,1), weight=1)
FRAME_OF_TITLE.rowconfigure(0, weight=1)

LABEL_OF_TITLE = ctk.CTkLabel(FRAME_OF_TITLE, text="Title")
ENTRY_OF_TITLE = ctk.CTkEntry(FRAME_OF_TITLE, placeholder_text="Title...", placeholder_text_color="#a1c1e3")

LABEL_OF_TITLE.grid(row=0, column=0, sticky="e",padx=5)
ENTRY_OF_TITLE.grid(row=0, column=1, sticky="w",padx=5)



FRAME_OF_CHANNELS_SELECTION = ctk.CTkFrame(CTC_TAB, height=10, fg_color="#3D3C3A")
FRAME_OF_CHANNELS_SELECTION.pack(padx=5, pady=5, fill="both", expand=True)
FRAME_OF_CHANNELS_SELECTION.columnconfigure((0,1,2,3), weight=1)
FRAME_OF_CHANNELS_SELECTION.rowconfigure(0, weight=1)

input_options = ['In 1', 'In 2', 'In 3', 'In 4']
output_options = ['Out 1', 'Out 2']

LABEL_OF_INPUT_CHANNEL = ctk.CTkLabel(FRAME_OF_CHANNELS_SELECTION, text="Input Channel")
LABEL_OF_OUTPUT_CHANNEL = ctk.CTkLabel(FRAME_OF_CHANNELS_SELECTION, text="Output Channel")

ENTRY_OF_INPUT_CHANNEL = ctk.StringVar(value="In 1")
DROPDOWN_OF_INPUT_CHANNEL = ctk.CTkComboBox(FRAME_OF_CHANNELS_SELECTION, values=input_options, variable=ENTRY_OF_INPUT_CHANNEL)
ENTRY_OF_INPUT_CHANNEL.set("In 1")

ENTRY_OF_OUTPUT_CHANNEL = ctk.StringVar(value="Out 2")
DROPDOWN_OF_OUTPUT_CHANNEL = ctk.CTkComboBox(FRAME_OF_CHANNELS_SELECTION, values=output_options, variable=ENTRY_OF_OUTPUT_CHANNEL)
ENTRY_OF_OUTPUT_CHANNEL.set("Out 2")

LABEL_OF_INPUT_CHANNEL.grid(row=0, column=0, sticky="e",padx=5)
DROPDOWN_OF_INPUT_CHANNEL.grid(row=0, column=1, sticky="w",padx=5)
LABEL_OF_OUTPUT_CHANNEL.grid(row=0, column=2, sticky="e",padx=5)
DROPDOWN_OF_OUTPUT_CHANNEL.grid(row=0, column=3, sticky="w",padx=5)


FRAME_OF_POWER_CONTROLS = ctk.CTkFrame(CTC_TAB, height=10, fg_color="#3D3C3A",)
FRAME_OF_POWER_CONTROLS.pack(padx=5, pady=5, fill="both", expand=True)

FRAME_OF_POWER_CONTROLS.columnconfigure((0,1,2,3), weight=1)
FRAME_OF_POWER_CONTROLS.rowconfigure((0,1), weight=1)


LABEL_OF_LOW_POWER_LIMIT = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="Low Limit")
LABEL_OF_HIGH_POWER_LIMIT = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="High Limit")
LABEL_OF_MAXIMUM_POWER_LIMIT = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="Max Limit")
LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="Increase by")
ENTRY_OF_LOW_POWER_LIMIT = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...")
ENTRY_OF_HIGH_POWER_LIMIT = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...")
ENTRY_OF_MAXIMUM_POWER_LIMIT = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...")
ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...")

LABEL_OF_LOW_POWER_LIMIT.grid(row=0, column=0, sticky="e",padx=5, pady=5)
LABEL_OF_HIGH_POWER_LIMIT.grid(row=0, column=2, sticky="e",padx=5, pady=5)
LABEL_OF_MAXIMUM_POWER_LIMIT.grid(row=1, column=2, sticky="e",padx=5, pady=5)
LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row=1, column=0, sticky="e",padx=5, pady=5)
ENTRY_OF_LOW_POWER_LIMIT.grid(row=0, column=1, sticky="w",padx=5, pady=5)
ENTRY_OF_HIGH_POWER_LIMIT.grid(row=0, column=3, sticky="w",padx=5, pady=5)
ENTRY_OF_MAXIMUM_POWER_LIMIT.grid(row=1, column=3, sticky="w",padx=5, pady=5)
ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row=1, column=1, sticky="w",padx=5, pady=5)



FRAME_OF_PID = ctk.CTkFrame(CTC_TAB, height=10, fg_color="#3D3C3A")
FRAME_OF_PID.pack(padx=5, pady=5, fill="both", expand=True)

FRAME_OF_PID.columnconfigure((0,1,2,3,4,5), weight=1)
FRAME_OF_PID.rowconfigure(0, weight=1)

LABEL_OF_P_VALUE_OF_CTC = ctk.CTkLabel(FRAME_OF_PID, text="P")
LABEL_OF_I_VALUE_OF_CTC = ctk.CTkLabel(FRAME_OF_PID, text="I")
LABEL_OF_D_VALUE_OF_CTC = ctk.CTkLabel(FRAME_OF_PID, text="D")
ENTRY_OF_P_VALUE_OF_CTC = ctk.CTkEntry(FRAME_OF_PID)
ENTRY_OF_H_VALUE_OF_CTC = ctk.CTkEntry(FRAME_OF_PID)
ENTRY_OF_D_VALUE_OF_CTC = ctk.CTkEntry(FRAME_OF_PID)

LABEL_OF_P_VALUE_OF_CTC.grid(row=0, column=0, sticky="e",padx=5)
LABEL_OF_I_VALUE_OF_CTC.grid(row=0, column=2, sticky="e",padx=5)
LABEL_OF_D_VALUE_OF_CTC.grid(row=0, column=4, sticky="e",padx=5)
ENTRY_OF_P_VALUE_OF_CTC.grid(row=0, column=1, sticky="w",padx=5)
ENTRY_OF_H_VALUE_OF_CTC.grid(row=0, column=3, sticky="w",padx=5)
ENTRY_OF_D_VALUE_OF_CTC.grid(row=0, column=5, sticky="w",padx=5)


FRAME_OF_TEMPERATURE_CONTROLS = ctk.CTkFrame(CTC_TAB, height=10, fg_color="#3D3C3A")
FRAME_OF_TEMPERATURE_CONTROLS.pack(padx=5, pady=5, fill="both", expand=True)

FRAME_OF_TEMPERATURE_CONTROLS.columnconfigure((0,1,2,3), weight=1)
FRAME_OF_TEMPERATURE_CONTROLS.rowconfigure((0,1,2,3), weight=1)

LABEL_OF_START_TEMPERATURE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Start\nTemperature")
LABEL_OF_STOP_TEMPERATURE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Stop\nTemperature")
LABEL_OF_INCREASING_INTERVAL_OF_TEMPERATURE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Increase\nTemperature by")
LABEL_OF_THRESHOLD = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Threshold")
LABEL_OF_TOLERANCE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Tolerance")
LABEL_OF_DELAY_OF_CTC = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Delay of CTC")

ENTRY_OF_START_TEMPERATURE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
ENTRY_OF_STOP_TEMPERATURE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
ENTRY_OF_THRESHOLD = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
ENTRY_OF_TOLERANCE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
ENTRY_OF_DELAY_OF_CTC = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Seconds...")

COMPLETE_CYCLE = tk.IntVar(value=0)
COMPLETE_CYCLE_CHECKBUTTON = ctk.CTkSwitch(FRAME_OF_TEMPERATURE_CONTROLS, text="Complete Cycle", variable=COMPLETE_CYCLE, onvalue=1, offvalue=1)

LABEL_OF_START_TEMPERATURE.grid(row=0, column=0, sticky="e",padx=5, pady=5)
LABEL_OF_STOP_TEMPERATURE.grid(row=1, column=0, sticky="e",padx=5, pady=5)
LABEL_OF_INCREASING_INTERVAL_OF_TEMPERATURE.grid(row=2, column=0, sticky="e",padx=5, pady=5)
LABEL_OF_THRESHOLD.grid(row=0, column=2, sticky="e",padx=5, pady=5)
LABEL_OF_TOLERANCE.grid(row=1, column=2, sticky="e",padx=5, pady=5)
LABEL_OF_DELAY_OF_CTC.grid(row=2, column=2, sticky="e",padx=5, pady=5)
ENTRY_OF_START_TEMPERATURE.grid(row=0, column=1, sticky="w",padx=5, pady=5)
ENTRY_OF_STOP_TEMPERATURE.grid(row=1, column=1, sticky="w",padx=5, pady=5)
ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE.grid(row=2, column=1, sticky="w",padx=5, pady=5)
ENTRY_OF_THRESHOLD.grid(row=0, column=3, sticky="w",padx=5, pady=5)
ENTRY_OF_TOLERANCE.grid(row=1, column=3, sticky="w",padx=5, pady=5)
ENTRY_OF_DELAY_OF_CTC.grid(row=2, column=3, sticky="w",padx=5, pady=5)
COMPLETE_CYCLE_CHECKBUTTON.grid(row=3,column=0,columnspan=4)


CURRENT_SOURCE_TAB.rowconfigure(0, weight=2)
CURRENT_SOURCE_TAB.rowconfigure(1, weight=3)
CURRENT_SOURCE_TAB.columnconfigure((0), weight=1, uniform='a')

CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME = ctk.CTkFrame(CURRENT_SOURCE_TAB, fg_color="#3D3C3A")
CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME.rowconfigure((0,1), weight=1)
CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME.columnconfigure((0,1,2,3), weight=1)

START_CURRENT_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Start Current")
STOP_CURRENT_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Stop Current")
INCREASE_CURRENT_BY_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Increase\nCurrent by")
CURRENT_SOURCE_DELAY_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Delay of\nCurrent Source")

ENTRY_OF_START_CURRENT = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")
ENTRY_OF_STOP_CURRENT = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")
ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")
ENTRY_OF_DELAY_OF_CURRENT_SOURCE = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")

START_CURRENT_LABEL.grid(row=0, column=0, sticky="e", padx=5, pady=5)
STOP_CURRENT_LABEL.grid(row=1, column=0, sticky="e", padx=5, pady=5)
INCREASE_CURRENT_BY_LABEL.grid(row=0, column=2, sticky="e", padx=5, pady=5)
CURRENT_SOURCE_DELAY_LABEL.grid(row=1, column=2, sticky="e", padx=5, pady=5)

ENTRY_OF_START_CURRENT.grid(row=0, column=1, sticky="w", padx=5, pady=5)
ENTRY_OF_STOP_CURRENT.grid(row=1, column=1, sticky="w", padx=5, pady=5)
ENTRY_OF_NUMBER_OF_CURRENT_INTERVALS.grid(row=0, column=3, sticky="w", padx=5, pady=5)
ENTRY_OF_DELAY_OF_CURRENT_SOURCE.grid(row=1, column=3, sticky="w", padx=5, pady=5)

CURRENT_SOURCE_TIME_INPUTS_FRAME = ctk.CTkFrame(CURRENT_SOURCE_TAB, fg_color="#3D3C3A")
CURRENT_SOURCE_TIME_INPUTS_FRAME.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
CURRENT_SOURCE_TIME_INPUTS_FRAME.rowconfigure((0,1,2,3), weight=1)
CURRENT_SOURCE_TIME_INPUTS_FRAME.columnconfigure((0,1,2,3,4,5), weight=1)

SELECTED_TEMPERATURES_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Required\nTemperatures")
MEASURING_TIME_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Total Time")
HIGH_PULSE_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="High Pulse")
LOW_PULSE_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Low Pulse")
PULSE_WIDTH_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Pulse Width")
NUMBER_OF_PULSES_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="No. of Pulses\nper second")

TEMPERATURES_ENTRY = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="eg. 234,456,600")
MEASURING_TIME_ENTRY = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Ampere...")
ENTRY_OF_HIGH_PULSE = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Ampere...")
ENTRY_OF_LOW_PULSE = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Ampere...")
ENTRY_OF_PULSE_WIDTH = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Ampere...")
ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="eg.3")

SELECTED_TEMPERATURES_LABEL.grid(padx=5, pady=5, row=0, column=0, sticky="e")
MEASURING_TIME_LABEL.grid(padx=5, pady=5, row=0, column=2, sticky="e")
HIGH_PULSE_LABEL.grid(padx=5, pady=5, row=1, column=0, sticky="e")
LOW_PULSE_LABEL.grid(padx=5, pady=5, row=2, column=0, sticky="e")
PULSE_WIDTH_LABEL.grid(padx=5, pady=5, row=1, column=2, sticky="e")
NUMBER_OF_PULSES_LABEL.grid(padx=5, pady=5, row=2, column=2, sticky="e")

TEMPERATURES_ENTRY.grid(padx=5, pady=5, row=0, column=1, sticky="w")
MEASURING_TIME_ENTRY.grid(padx=5, pady=5, row=0, column=3, sticky="w")
ENTRY_OF_HIGH_PULSE.grid(padx=5, pady=5, row=1, column=1, sticky="w")
ENTRY_OF_LOW_PULSE.grid(padx=5, pady=5, row=2, column=1, sticky="w")
ENTRY_OF_PULSE_WIDTH.grid(padx=5, pady=5, row=1, column=3, sticky="w")
ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND.grid(padx=5, pady=5, row=2, column=3, sticky="w")

FRAME_OF_GRAPH = ctk.CTkFrame(GRAPH_TAB, fg_color="#3D3C3A")
FRAME_OF_GRAPH.pack(padx=10, pady=(5,0), fill="both", expand=True)

CHOOSEN_TEMPERATURE = ctk.StringVar(value='200K')
CHOOSE_TEMPERATURE_COMBOBOX = ctk.CTkComboBox(FRAME_OF_GRAPH, values=["200K", "300K", "500K"], variable=CHOOSEN_TEMPERATURE)
CHOOSE_TEMPERATURE_COMBOBOX.pack(pady=(10,0))
GRAPH_TITLE_LABEL = ctk.CTkLabel(FRAME_OF_GRAPH, text = "Resistance Vs Temperature", font=('Times', 32))
GRAPH_TITLE_LABEL.pack(pady=5)


plt.style.use("dark_background")
FIGURE_OF_GRAPH = plt.figure(facecolor="black", edgecolor="white") # Created a figure to add graph

CANVAS_OF_GRAPH = FigureCanvasTkAgg(FIGURE_OF_GRAPH,master=FRAME_OF_GRAPH) # Created a canvas to plot graph
CANVAS_OF_GRAPH.get_tk_widget().pack(padx=10, pady=(5,0), fill="both", expand=True)
GRAPH = FIGURE_OF_GRAPH.add_subplot(111)

GRAPH.set_xlabel("TEMPERATURE")
GRAPH.set_ylabel("RESISTANCE")
GRAPH.grid() # Added grids to graph
GRAPH.axhline(linewidth=3) # Added X axis
GRAPH.axvline(linewidth=3) # Added Y axis

TOOLBAR_OF_GRAPH = NavigationToolbar2Tk(CANVAS_OF_GRAPH, FRAME_OF_GRAPH) # Added toolbar for graph
TOOLBAR_OF_GRAPH.pan()

INTERFACE.mainloop()