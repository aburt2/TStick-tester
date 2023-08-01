


# Standard libraries
from subprocess import Popen, run,PIPE
import time
import sys
import serial
import numpy as np
import pandas as pd

BAUDRATE = "115200"
READ_TIMEOUT_SECS = 5.0

DATA_START = b'<<<'
DATA_END = b'\n'

# Ports
rxPort = 'COM8'
dur = 60
board = 'tinypico'

# Setup testing parameters
poll_delay = 100

# Setup Threads
p1 = Popen(['python', './ReadCOM.py', rxPort, BAUDRATE, str(dur)], stdout=PIPE,text=True) 
# p2 = Popen(['python', './ReadCOM.py', rxPort, BAUDRATE, str(dur)], stdout=PIPE,text=True)

start_time = time.perf_counter()
cur_time = 0

while ((p1.poll() is None)):
    print("Still working...")
    # sleep a while
    # time_passed = time.perf_counter()-start_time
    # if np.mod(time_passed,10) < 0.01:
    #     print("messages received from TX: %s" % p1.stdout.readline()) # print output from ReadCOM.py for rx
    #     print("messages received from RX: %s" % p2.stdout.readline()) # print output from ReadCOM.py for tx
    # txCount = p1.stdout.read(1)
    # rxCount = p2.stdout.read(1)
    # print("messages received from TX: %s" % p1.stdout.read(1)) # print output from ReadCOM.py for rx
    # print("messages received from RX: %s" % p2.stdout.read(1)) # print output from ReadCOM.py for tx
    cur_time = round(time.perf_counter()-start_time,2)
    print("Elapsed Time: " + str(cur_time) +"s")
    time.sleep(1)
    continue

print("Test Done, see files")

# Analyse Reliability
rxdf = pd.read_csv("messagesReceived_RX.csv")
# txdf = pd.read_csv("messagesReceived_TX.csv")

# Print Analysis
a = rxdf["Time"] # get time array
instLatency =  [x - a[i - 1] for i, x in enumerate(a)][1:]
reliability = 0
print("Messgaes Received: " + str(len(rxdf)))
print("Latency: " + str(reliability) + "%")

# Save results of analysis
reliabilityPD = pd.DataFrame({"Latency" : instLatency,"msg" : rxdf["Message"][0:-2]})
#fileName = "reliabilityResults/results_dur"+str(dur)+"_txdelay"+str(tx_delay)+"_msglength"+str(msg_length)+"_boardist"+str(board_dist)+pipeCond+".csv"
fileName = "formalResults/"+str(dur)+"_libmapperdelay"+board+"_board.csv"
#fileName = "occlusionResults2/txdelay"+str(tx_delay)+"_msglength"+str(msg_length)+"_boardist"+str(board_dist)+pipeCond+trial_num+".csv"
reliabilityPD.to_csv(fileName, encoding='utf-8', index=False)