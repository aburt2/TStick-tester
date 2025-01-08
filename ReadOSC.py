#requirements:
#python-osc
#wmill
#requests
#prometheus-client
#python-json-logger

import time
import os
import sys
import numpy as np
import pandas as pd


# OSC packages
from pythonosc.dispatcher import Dispatcher
from typing import List, Any
import asyncio

# Setup server
from pythonosc import osc_server

# Get osc parser
from pythonosc.parsing import ntp
from pythonosc.parsing import osc_types

# timing functions
import ntplib
from datetime import datetime,timedelta,timezone


# Initiate Dispatcher
disp = Dispatcher()

# Initialise lists
counter_list = []
loop_list = []
time_loop_list = []

# conversion
frac_secs = (1/2)**32
mcu_offset = -21038900 / 1000000

def get_tstick_debug(address: str, *args: List[Any]) -> None:
    # get time
    now = time.perf_counter_ns()

    # Append to list
    counter_list.append(int(args[0]))
    loop_list.append(int(args[1]))
    time_loop_list.append(now)

async def loop():
    # start time
    start_perf = time.perf_counter_ns()
    start_time = time.time()
    # Read config
    parentfolder = "data/enchantiW106"
    scenario = 3
    dur = 600

    # Create folder if parent folder does not exists
    if not os.path.exists(parentfolder):
        os.makedirs(parentfolder)

    # loop for time
    print("Start listening for OSC...")
    
    await asyncio.sleep(dur)
    
    print("Finished listening, Saving results")

    # Save results
    loopPd = pd.DataFrame({'Time' : time_loop_list,'Message' : loop_list})
    counterPd = pd.DataFrame({'Time' : time_loop_list,'Message' : counter_list}) 

    # Analyse Reliability
    period = 1e-3*loopPd["Time"].diff() # get time array
    instLatency = period - loopPd["Message"]
    instLatency[instLatency <= 0] = np.nan
    avgLatency = instLatency.mean(skipna=True)
    std = instLatency.std(skipna=True)

    # Print messages 
    print("Messgaes Received: " + str(len(loopPd)))
    print("Latency: " + str(np.round(avgLatency,2))  + u"\u00B1" + str(np.round(std, 2)) +" us")

    # # Save results of analysis
    reliabilityPD = pd.DataFrame({"Latency" : instLatency, "msg" : counterPd["Message"], "looptime": loopPd["Message"], "period":period, "time":loopPd["Time"]})
    fileName = parentfolder+"/"+"wifitests_"+str(scenario)+"_looptime.csv"
    reliabilityPD.to_csv(fileName, encoding='utf-8', index=False)


async def init_main():
    # OSC information
    ip = "0.0.0.0"
    osc_port = 8000

    # Set up dispatcher
    disp.map("/TStick_520/debug",get_tstick_debug)

    # Set up OSC Server
    server = osc_server.AsyncIOOSCUDPServer((ip,osc_port), disp, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    # Enter main loop
    await loop()
    
    # Close server after done
    transport.close()


asyncio.run(init_main())
