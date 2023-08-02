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

    # Get difference of time
    msgDif = filter_msg.diff()
    logicDif = np.where(msgDif > 0, 1, 0)
    missedDif = np.where(np.logical_and(msgDif>0,msgDif<0.02),1,0)

    # Calculate number of received messages, and missed messages
    rxmsg = sum(logicDif)
    missedmsg = len(msgDif)-sum(missedDif)
    reliability = 1 - missedmsg/len(msgDif)

    # Store in a dictionary
    reliabilityStats = dict({'rxmsg':rxmsg, 'missedmsg':missedmsg, 'reliability':reliability})

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
    avg = timedf['Latency'].mean()
    stdev = timedf['Latency'].std()

    # Get places without consecutive messages
    # timedf['consecutive'] = logicDif

    # Get array as a difference from the mean
    timedf['deviation'] = timedf['Latency'] - avg
    timedf['std_deviation'] = timedf['deviation']/stdev

    # Create plot and axis labels
    fig, axs = plt.subplots(2)

    # Plot Time
    timedf[['Latency','SMA10']].plot(ax=axs[0],label='Latency', figsize=(16,8))

    # Plot Deviation
    timedf[['deviation']].plot(ax=axs[1],label='Deviation', figsize=(16,8))

    # Plot parameters
    # Latency Plot parameters
    axs[0].set_ylabel('Latency (ms)')
    # Deviation Plot parameters
    axs[1].set_ylabel('Deviation from Mean (ms)')
    # Figure parameters
    titlestr = 'Latency of ' + board + ', Poll delay = ' + str(poll_delay) + ', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2))
    fig.suptitle(titlestr)

    # Save figure
    fig.savefig(pic_fileName)
    plt.close()

    # Print some statistics about this Data Set
    # Set up strings
    startstr = '\n************************************************'
    endstr = '************************************************\n'
    latencystr = 'Average Latency = ' + str(avg)
    rxmsgstr = 'Received Messages = ' + str(rxmsg)
    missedmsgstr = 'Missed Messages = ' + str(missedmsg)
    reliabilitystr = 'Packet Loss = ' + str(np.round(100*(1-reliability),2)) +'%'
    extremestr = 'Highest Latency = ' + str(max(timedf['Latency']))
    loweststr = 'Lowest Latency = ' + str(min(timedf['Latency']))
    print(startstr)
    print(titlestr)
    print(rxmsgstr)
    print(missedmsgstr)
    print(reliabilitystr)
    print(extremestr)
    print(loweststr)
    print(endstr)

    # Return the df
    return timedf, reliabilityStats

    

# Set test parameters
poll_delay = [0,50,100,200,500]
board = 'tinypico'
parentFolder = 'selfResults'

# Setup empty list
dataDf = []
relList = []
legendList = []
# Create axis object
fig, ax = plt.subplots()
xlim = 1e6
fig.suptitle('Latency Deviation for TinyPico accross different delays')
ax.set_ylabel('Number of Standard Deviations from Mean')

for delay in poll_delay:
    # Get time df from analysis
    tmpdf,tmpreliability = analyse_data(delay,board,parentFolder)
    dataDf.append(tmpdf)
    relList.append(tmpreliability)

    # Plto on axis
    avg = tmpdf['Latency'].mean()
    stdev = tmpdf['Latency'].std()
    legendstr = 'Poll delay = ' + str(delay) +', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2))
    legendList.append(legendstr)
    tmpdf[['std_deviation']].plot(ax=ax, label=legendstr, figsize=(16,8))

    # Get xlimit
    if len(tmpdf) < xlim:
        xlim = len(tmpdf)

# Show plot
ax.set_xlim(0,xlim)
ax.legend(legendList)
plt.show()
    







