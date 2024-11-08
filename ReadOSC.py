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

# Initiate Dispatcher
disp = Dispatcher()

# Initialise lists
counter_list = []
loop_list = []
time_loop_list = []
time_counter_list = []

def get_tstick_counter(address: str, *args: List[Any]) -> None:
    # get time
    now = time.perf_counter_ns()

    # Append to list
    counter_list.append(int(args[0]))
    time_counter_list.append(now)

def get_tstick_looptime(address: str, *args: List[Any]) -> None:
    # get time
    now = time.perf_counter_ns()

    # Append to list
    loop_list.append(int(args[0]))
    time_loop_list.append(now)

async def loop():
    # Read config
    parentfolder = "data/final_results"
    scenario = 2
    dur = 600

    # loop for time
    print("Start listening for OSC...")
    
    await asyncio.sleep(dur)
    
    print("Finished listening, Saving results")

    # Save results
    loopPd = pd.DataFrame({'Time' : time_loop_list,'Message' : loop_list})
    counterPd = pd.DataFrame({'Time' : time_counter_list,'Message' : counter_list}) 

    # Analyse Reliability
    period = 1e-3*loopPd["Time"].diff() # get time array
    instLatency = period - loopPd["Message"]
    instLatency[instLatency < 0] = 0
    avgLatency = instLatency.mean()

    # Print messages 
    print("Messgaes Received: " + str(len(loopPd)))
    print("Latency: " + str(avgLatency) + "s")

    # Save results of analysis
    reliabilityPD = pd.DataFrame({"Latency" : instLatency, "msg" : counterPd["Message"], "looptime": loopPd["Message"], "period":period, "time":loopPd["Time"]})
    fileName = parentfolder+"/"+"wifitests_"+str(scenario)+"_looptime.csv"
    reliabilityPD.to_csv(fileName, encoding='utf-8', index=False)


async def init_main():
    # OSC information
    ip = "0.0.0.0"
    osc_port = 8000

    # Set up dispatcher
    disp.map("/TStick_513/test/looptime",get_tstick_looptime)
    disp.map("/TStick_513/test/counter",get_tstick_counter)

    # Set up OSC Server
    server = osc_server.AsyncIOOSCUDPServer((ip,osc_port), disp, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    # Enter main loop
    await loop()
    
    # Close server after done
    transport.close()


asyncio.run(init_main())
