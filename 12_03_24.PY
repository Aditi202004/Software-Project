import pyvisa, serial, time
from telnetlib import Telnet


# rm = pyvisa.ResourceManager()
# nanovoltmeter = rm.open_resource('GPIB0::2::INSTR')
# current_source = serial.Serial('COM1', baudrate=9600,timeout=10)
ctc_device=Telnet("192.168.0.2",23,10)
# def send_command(command):
#     current_source.write((command+'\n').encode())
#     time.sleep(0.1)

# def read_response():
#     response = current_source.readline().decode().strip()
#     return response

def send_ctc_msg(msg): 
# This function is responsible for translating commands into valid format & sending commands to the CTC device
    
    response=None
    i=10
    while(not 0 and i>=0):
        try:
            ctc_device.write((msg+'\n').encode())
            response=ctc_device.read_until(b"\n",1).decode('ascii')
            break
        except:
            print("couldn't send message to ctc, trying again...")
            i-=1
            pass
    if(i<0):
        print("Couldn't send message to ctc even after max number of tries(10)")
    
    return response

def get_ctc_temp():
# Function to return the current temperature.
    i=20
    while(not 0 and i>=0):
        try:
            return float(send_ctc_msg('"channel.'+"In 1"+'?"'))
        except:
            i-=1
            pass
    raise Exception("Couldn't get temperature from ctc!")

# send_command("OUTP ON")  ## for setting output on
# send_command("SOUR:CURR:COMP 100") ## for setting compliance
# send_command("SOUR:CURR:RANG 0.00001") ## for setting range(maximum)--00.000uA
# send_command(":SYSTem:BEEPer:STATe ON") ## for setting beeping on
# send_command("SOUR:CURR 0.000000001") ## for setting current value
# nanovoltmeter.write(":SENSe:VOLTage:DC:RANGe 10") ## for setting range of the voltmeter

# voltage_result = nanovoltmeter.query("FETCh?") ## for getting voltage reading from the nanovoltmeter
# print(voltage_result)

send_ctc_msg('outputEnable on')



print("---------------")
# ifo = read_response()
# print(ifo)

