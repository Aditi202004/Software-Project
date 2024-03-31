import pyvisa
import time

rm = pyvisa.ResourceManager()
CURRENT_SOURCE = rm.open_resource('GPIB0::6::INSTR')

# CURRENT_SOURCE.write("*RST")

# CURRENT_SOURCE.write(("SOURce:PDELta:HIGH 10e-4"))
# CURRENT_SOURCE.write(("SOURce:PDELta:LOW 0"))
# CURRENT_SOURCE.write(("SOURce:PDELta:WIDTh 11e-3"))
# # CURRENT_SOURCE.write(("SOUR:PDEL:COUN 30"))
# CURRENT_SOURCE.write(("UNIT:VOLT:DC OHMS"))
wid = CURRENT_SOURCE.query("SOUR:PDEL:WIDT?")
print(wid)
CURRENT_SOURCE.write(("SOURce:PDELta:ARM"))
CURRENT_SOURCE.write(("INIT:IMM"))
time.sleep(11.5) # time + 1.50
CURRENT_SOURCE.write(("SOUR:SWE:ABOR"))

data = CURRENT_SOURCE.query("TRACe:DATA?")
print(data)
print(len(data))

data = data[:-1].split(",")
res = []
Time = []
for i,dat in enumerate(data):
    if(i%2==0):
        res.append(float(dat))
    else:
        Time.append(float(dat))
print(res)
print(Time)























# CURRENT_SOURCE = rm.open_resource('GPIB0::6::INSTR')
# print(CURRENT_SOURCE)
# NANOVOLTMETER = serial.Serial('COM1', baudrate=9600,timeout=10)



# # CURRENT_SOURCE.write("*RST")

# CURRENT_SOURCE.write(("OUTP ON"))

# CURRENT_SOURCE.write(("SOURce:PDELta:HIGH 10e-4"))
# CURRENT_SOURCE.write(("SOURce:PDELta:LOW 0"))
# CURRENT_SOURCE.write(("SOURce:PDELta:WIDTh 11e-3"))
# CURRENT_SOURCE.write(("SOURce:PDELta:ARM"))
# CURRENT_SOURCE.write(("INIT:IMM"))






# CURRENT_SOURCE.write(("OUTP ON").encode())
# # start = time.time()
# CURRENT_SOURCE.write("SOUR:CURR 0.01".encode())
# time.sleep(1)
# CURRENT_SOURCE.write("SOUR:CURR 0".encode())
# # time.sleep(0.4)
# vol = []
# for i in range(1000):
#     vol.append(float(NANOVOLTMETER.query("FETCh?")))



# end = time.time()
# # print(end-start)
# time.sleep(0.3)
# start = time.time()
# end = time.time()
# print(end-start)

# print(vol)
# print(max( vol))
# CURRENT_SOURCE.write(("OUTP ON").encode())



















# rm = pyvisa.ResourceManager()
# NANOVOLTMETER = rm.open_resource('GPIB0::2::INSTR')

# CURRENT_SOURCE = serial.Serial('COM1', baudrate=9600,timeout=10)
# CURRENT_SOURCE.write(("*RST").encode())
# CURRENT_SOURCE.write(("OUTP ON").encode())
# # CURRENT_SOURCE.write("SOUR:CURR 0.01".encode())
# CURRENT_SOURCE.write(("SOURce:PDELta:HIGH 10e-4").encode())
# CURRENT_SOURCE.write(("SOURce:PDELta:LOW 0").encode())
# CURRENT_SOURCE.write(("SOURce:PDELta:WIDTh 11e-3").encode())
# CURRENT_SOURCE.write(("SOURce:PDELta:ARM").encode())
# CURRENT_SOURCE.write(("INIT:IMM").encode())

# CURRENT_SOURCE.write(("SOUR:PDEL:SDEL 11e-3").encode())
# voltage = []
# for i in range(20):
# #     CURRENT_SOURCE.write(("SOUR:PDEL:WIDT 11e-3").encode())
# #     CURRENT_SOURCE.write(("SOUR:PDEL:SDEL 11e-3").encode())
#     voltage.append(float(NANOVOLTMETER.query("FETCh?")))
# #     # print(i)
# CURRENT_SOURCE.write(("SOUR:PDEL:COUN 2000").encode())




# print(voltage)
# # CURRENT_SOURCE.write(("OUTP OFF").encode())






