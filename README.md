# Software-Project

## Introduction
The product is designed for measuring the temperature dependence of resistance in various sample materials.
Our software eliminates the need for manual input parameter adjustments on the measuring device.
Unlike conventional experimentation methods that necessitate manual adjustment of input parameters such as
current and voltage on the measuring device, our software eliminates this labor-intensive step while ensuring
precision in data collection. The resistance vs time mode plots the graph between resistance that varies 
with increasing time at a particular temperature. The resistance vs temperature mode plots the graph between resistance varying with
change in temperature.

## Setting Up and Performing the Experiment
- First, check if the connections are proper or not.
  - Check if the RS-232 port, the GPIB port and the Telnet port are properly connected to the hardware.
- Select the type of experiment you want to perform.
  - Resistance vs Time
  - Resistance vs Temperature
  - Note: you can select both modes at the same time also.
- Resistance vs Time mode
  - Input for the CTC:
    - Title: the name of the file to be stored.
    - Input channel: the channel through which input is provided.
    - Output channel: the channel through which output will be recorded.
    - Low limit: low limit of power (in Watts).
    - High limit: high limit of power (in Watts).
    - Increase by: the value by which power is to be increased (in Watts).
    - Max limit: maximum power that CTC can supply to increase by any temperature (in Watts).
    - P: P-value.
    - I: I-value.
    - D: D-value.
    - Threshold: error allowed for achieving the final value of temperature at which reading is to be taken (in Kelvin).
    - Tolerance: error allowed for stabilizing to the final value of temperature at which reading is to be taken (in Kelvin).
  - Input for current source:
    - High pulse: value of high pulse (in Ampere).
    - Low pulse: value of low pulse (in Ampere).
    - Total time: total time for which resistance is to be plotted.
    - Pulse width: wavelength of a single pulse (in seconds).
    - Number of pulses per second: number of pulses that will pass through in one second.
  - Required temperatures: temperatures at which resistance is to be plotted.
- Resistance vs Temperature mode
  - Input for the CTC:
    - Title: the name of the file to be stored.
    - Input channel: the channel through which input is provided.
    - Output channel: the channel through which output will be recorded.
    - Low limit: low limit of power (in Watts).
    - High limit: high limit of power (in Watts).
    - Increase by: the value by which power is to be increased (in Watts).
    - Max limit: maximum power that CTC can supply to increase by any temperature (in Watts).
    - P: P-value.
    - I: I-value.
    - D: D-value.
    - Start temp: the temperature from which you wish to begin to take readings from (in Kelvin).
    - Stop temp: the temperature at which you wish to stop the readings (in Kelvin).
    - Increase temp by: interval by which temperature is to be increased (in Kelvin).
    - Threshold: error allowed for achieving the final value of temperature at which reading is to be taken (in Kelvin).
    - Tolerance: error allowed for stabilizing to the final value of temperature at which reading is to be taken (in Kelvin).
    - Delay of CTC: delay after which CTC will start increasing the temperature (in seconds).
    - Complete cycle: if this button is clicked, the experiment will perform both heating and cooling cycle.
  - Input for the current source:
    - Start current: minimum value of current that will be passed.
    - Stop current: maximum value of current that will be passed.
    - Increase current by: value by which current will be increased from start to stop current.
    - Delay of current source: delay after which current source will start supplying current to the sample.
  - If both the modes are selected, give the inputs accordingly as stated above.
- After that, click the Sync Set button to set all the values.
  - Note: you may also click the Sync Get button to use values from the previous experiment.
- Then, click the Trigger button to begin the experiment.
- If you wish to stop the experiment while it is still running, you can click the Abort button.

## Other Details
- If you wish to receive an email on completion of the experiment, click the corresponding button in the CTC tab.
- Click the Settings button to fill in your email ID.
- An email will be sent by the system to you on this email ID after the experiment is completed.
