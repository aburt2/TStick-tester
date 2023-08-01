import sys
import serial
import time
import numpy as np
import pandas as pd
import os

ser = serial.Serial(port=sys.argv[1],baudrate=int(sys.argv[2]),timeout=5)
dur = int(sys.argv[3])
count = 0
start_time = time.perf_counter()
cur_time = 0
DATA_END = b'\n'

serialPd = pd.DataFrame({'Time' : [],'Message' : []})
timeList = []
msgList = []

# Define filename for saving
fileName = "messagesReceived_"

# Determine if it is the transmitter or receiver we are connected to
if sys.argv[1] == 'COM11':
    device = "TX.csv"
else:
    device = "RX.csv"

# Update filename
fileName = fileName + device

# Check if the file exists and delete it if it does
if os.path.exists(fileName):
    os.remove(fileName)
 
    
while (time.perf_counter()-start_time<dur): # The program never ends... will be killed when master is over.
    # sys.stdin.readline()
    output = ser.read_until(expected=DATA_END) # read output
    timeList.append(time.perf_counter())
    msgList.append(output)
    # time.sleep(1)

# Close port    
ser.close()
print("Finished test, saving results")

# Save data
serialPd.Time = timeList
serialPd.Message = msgList
serialPd.to_csv(fileName,encoding='utf-8', index=False)
