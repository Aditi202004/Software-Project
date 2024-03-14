
# Required imports for connecting the device
import pyvisa, serial, telnetlib

# Other Required imports
import time, csv




# Note :- We have used Ethernet cable for CTC device, GPIB cable for Nanovoltmeter, RS232 cable for AC/DC current source. The code may change if you use different cables... :)


global NANOVOLTMETER, CURRENT_SOURCE, CTC

global MAX_RETRY, INPUT_CHANNEL_OF_CTC, TOLERANCE, OUTPUT_CHANNEL_OF_CTC, HIGH_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC, THRESHOLD, START_CURRENT, INCREASING_INTERVAL_OF_CURRENT, START_TEMPERATURE, END_TEMPERATURE, DELAY_OF_CTC, INCREASING_INTERVAL_OF_TEMPERATURE, COMPLETE_CYCLE, CSV_FILE

RESISTANCE_VALUES = [] # Array to store resistances at all temperatures...

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
def ACHIVE_AND_STABILIZE_TEMPERATURE(required_temperature): 
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
                raise Exception("Cannot achive all the temperatures by given Maximum limit of Power")
            
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
        ACHIVE_AND_STABILIZE_TEMPERATURE(present_temperature) 

        time.sleep(DELAY_OF_CTC) # Delaying some time...

        # Getting current resistance of the sample at current temmperature...
        present_resistance = GET_PRESENT_RESISTANCE() 

        # Writing the present temperature and resistance into csv file...
        WRITE_DATA_TO_CSV(present_temperature, present_resistance)

        present_temperature += INCREASING_INTERVAL_OF_TEMPERATURE * direction


    SEND_COMMAND_TO_CTC("outputEnable off")


def TRIGGER():
    global MAX_RETRY, INPUT_CHANNEL_OF_CTC, TOLERANCE, OUTPUT_CHANNEL_OF_CTC, HIGH_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC, THRESHOLD, START_CURRENT, INCREASING_INTERVAL_OF_CURRENT, START_TEMPERATURE, END_TEMPERATURE, DELAY_OF_CTC, INCREASING_INTERVAL_OF_TEMPERATURE, COMPLETE_CYCLE, CSV_FILE

    # Connecting CTC, Nanovoltmeter and AC/DC Current Source... The function is defined above...
    CONNECT_INSTRUMENTS()

    # Getting resistances from starting temperature to end temperature(forward cycle)... The function is defined above...
    GET_RESISTANCE_AT_ALL_TEMPERATURES(START_TEMPERATURE, END_TEMPERATURE)
    
    if COMPLETE_CYCLE : GET_RESISTANCE_AT_ALL_TEMPERATURES(END_TEMPERATURE, START_TEMPERATURE)