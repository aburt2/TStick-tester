# Standard packages
import time
import os
import sys

# Sending serial commands
import serial

# Math
import numpy as np
import pandas as pd

# OSC packages
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from typing import List, Any

# Initiate Dispatcher
disp = Dispatcher()
trial_num = int(sys.argv[2])
count = 0
start_time = time.perf_counter()
cur_time = 0
DATA_END = b'\n'
sent_time = 0
msgList = []
serlatencyList = []

def get_tstick_debug(address: str, *args: List[Any]) -> None:
    # Append to list
    msgList.append(int(args[0]))


# Set up dispatcher
disp.map("/TStick_520/test/looptime",get_tstick_debug)

# Read config
parentfolder = "data/enchantiW106"
scenario = 3

# Lists
sentList = []
revList = []

# Create folder if parent folder does not exists
if not os.path.exists(parentfolder):
    os.makedirs(parentfolder)

# Set up OSC Server
server_ip = "0.0.0.0"
osc_port = 8000
server = BlockingOSCUDPServer((server_ip, osc_port), disp)

# Setup serial port
ser = serial.Serial(port=sys.argv[1],baudrate=115200,timeout=5)

# Make sure wifi power saving mode is off
print(" Turning off wifi power saving mode")
ser.write(bytes(b'wifi ps off\r\n'))
time.sleep(1) # wait to ensure command was received

# loop for time
print("Start listening for OSC...")

sent_time = time.perf_counter_ns()
for trial in range(0,trial_num+1): # The program never ends... will be killed when master is over.
    # sys.stdin.readline()
    ser.write(bytes(b'osc ping\r\n'))
    sentList.append(time.perf_counter_ns())
    server.handle_request()
    revList.append(time.perf_counter_ns())
    time.sleep(0.1)

# Close port    
ser.close()
print("Finished listening, Saving results")

# ignore the first entry
sentList = sentList[1:]
revList = revList[1:]
msgList = msgList[1:]

print("Messages Requested: " + str(len(sentList)))
print("Messages Received: " + str(len(revList)))

# Save results
loopPd = pd.DataFrame({"Sent_time" : sentList, "Rev_time" : revList, "Message" : msgList})

# Analyse Reliability
instLatency = abs(loopPd["Rev_time"] - loopPd["Sent_time"])*1e-6
instLatency = instLatency - (loopPd["Message"]*1e-3)
instLatency[instLatency <= 0] = 0
avgLatency = instLatency.mean(skipna=True)
std = instLatency.std(skipna=True)

# Print messages 
print("Latency: " + str(np.round(avgLatency,2))  + u"\u00B1" + str(np.round(std, 2)) +"ms")
print("Average looptime: " + str(loopPd["Message"].mean() * 1e-3) + "ms")

# # Save results of analysis
reliabilityPD = pd.DataFrame({"Latency" : instLatency, "looptime": loopPd["Message"] })
fileName = parentfolder+"/"+"wifitests_"+str(scenario)+"_latency.csv"
reliabilityPD.to_csv(fileName, encoding='utf-8', index=False)

