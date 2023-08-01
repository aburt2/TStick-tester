import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import math

# Define some analysis functions
def analyse_data(poll_delay,board,parent_folder):
    '''
    Do some basic analysis on the wifi data
    '''
    # construct filename
    fileName = parent_folder+"/"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"
    pic_fileName = parent_folder+"/"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.png"
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
    logicDif = np.where(msgDif <= 0.02, True, False)

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
    timedf['SMA10'] = timedf.rolling(10).mean()
    timedf['SMA10'].dropna(inplace=True)

    # Get average and standard deviation
    avg = tmpdf['Latency'].mean()
    stdev = tmpdf['Latency'].std()
    legendstr = 'Poll delay = ' + str(delay) +', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2))

    # Get places without consecutive messages
    # timedf['consecutive'] = logicDif

    # Get array as a difference from the mean
    timedf['deviation'] = timedf['Latency'] - avg

    # Create plot and axis labels
    fig, axs = plt.subplots(2)

    # Plot Time
    timedf[['Latency','SMA10']].plot(ax=axs[0],label='Latency', figsize=(16,8))
    titlestr = 'Latency of ' + board + ', Poll delay = ' + str(poll_delay)

    # Plot Deviation
    timedf[['deviation']].plot(ax=axs[1],label='Deviation', figsize=(16,8))
    titlestr = 'Latency of ' + board + ', Poll delay = ' + str(poll_delay)

    # Plot parameters
    # Latency Plot parameters
    axs[0].set_ylabel('Latency (ms)')
    # Deviation Plot parameters
    axs[1].set_ylabel('Deviation from Mean (ms)')
    # Figure parameters
    fig.suptitle(titlestr)

    # Save figure
    fig.savefig(pic_fileName)
    plt.close()

    # Return the df
    return timedf

    

# Set test parameters
poll_delay = [0,50,100,200,500]
board = 'tinypico'
parentFolder = 'selfResults'

# Setup empty list
dataDf = []
legendList = []
# Create axis object
fig, ax = plt.subplots()
xlim = 1e6
fig.suptitle('Latency Deviation for TinyPico accross different delays')
ax.set_ylabel('Deviation from Mean (ms)')

for delay in poll_delay:
    # Get time df from analysis
    tmpdf = analyse_data(delay,board,parentFolder)
    dataDf.append(tmpdf)

    # Plto on axis
    avg = tmpdf['Latency'].mean()
    stdev = tmpdf['Latency'].std()
    legendstr = 'Poll delay = ' + str(delay) +', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2))
    legendList.append(legendstr)
    tmpdf[['deviation']].plot(ax=ax, label=legendstr, figsize=(16,8))

    # Get xlimit
    if len(tmpdf) < xlim:
        xlim = len(tmpdf)

# Show plot
ax.set_xlim(0,xlim)
ax.legend(legendList)
plt.show()
    







