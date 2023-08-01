import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

# Set test parameters
poll_delay = 0
board = 'tinypico'


# construct filename
fileName = "formalResults/"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"

# Open test daya
rxdf = pd.read_csv(fileName)

# Plot data
time = rxdf["Latency"]*100 # convert latency to ms
msg = rxdf["msg"] # grab messages

# Filter out 0s
filter_msg = msg[msg>0]
filter_time = time[msg>0]

# # Print these out
print(filter_msg)
# print(filter_time)

# Get difference of time
msgDif = filter_msg.diff()
logicDif = np.where(msgDif <= 0.01, True, False)
print(logicDif)

# Plot Time
plt.scatter(filter_time)


