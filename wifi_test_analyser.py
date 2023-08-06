import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import math

# Set test parameters
poll_delay = 0
board = 'sparkfun'


# construct filename
fileName = "longResults/"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"

# Open test daya
rxdf = pd.read_csv(fileName)

# Plot data
time = rxdf["Latency"]*1000 # convert latency to ms
msg = rxdf["msg"] # grab messages

# Filter out 0s
filter_msg = msg[msg>0]
filter_time = time[msg>0]

# # Print these out
# print(filter_msg)
# print(filter_time)

# Get difference of time
msgDif = filter_msg.diff()
logicDif = np.where(msgDif > 0, True, False)
# Compute latency taking into account missed messages
time_list = filter_time.to_list()
new_latency = []
idx = 1
tmp = 0
while idx < len(time_list):
    # Increment temperary value
    
    if not math.isnan(time_list[idx]):
        tmp += time_list[idx]
    if logicDif[idx]:
        new_latency.append(tmp) # add if consecutive
        tmp = 0
    # Increment index
    idx += 1  

# Get rolling average of latency
timedf = pd.DataFrame({'Latency':new_latency})
timedf['SMA100'] = timedf.rolling(100).mean()
timedf['SMA100'].dropna(inplace=True)

# Get places without consecutive messages
# timedf['consecutive'] = logicDif

# Get array as a difference from the mean
timedf['deviation'] = (timedf['SMA100'] - timedf['SMA100'].mean())/(timedf['SMA100'].std())

# Create plot and axis labels
fig, axs = plt.subplots(2)

# Plot Time
timedf[['SMA100']].plot(ax=axs[0],label='Latency', figsize=(16,8))
titlestr = 'Latency of ' + board + ', Poll delay = ' + str(poll_delay)

# Plot Deviation
timedf[['deviation']].plot(ax=axs[1],label='Deviation', figsize=(16,8))
titlestr = 'Latency of ' + board + ', Poll delay = ' + str(poll_delay)

# Plot parameters
# Latency Plot parameters
axs[0].set_ylabel('Latency (ms)')
# Deviation Plot parameters
axs[1].set_ylabel('Deviation from Mean (num of std)')
# Figure parameters
fig.suptitle(titlestr)

# Save figure
fig.savefig('test.png')
# plt.show()

