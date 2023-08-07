import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
import os

# Define some analysis functions
def analyse_data(poll_delay,board,parent_folder,dur='60 seconds',window="1s"):
    '''
    Do some basic analysis on the wifi data
    '''
    # Construct file names
    fileName = parent_folder+"/"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"
    pic_fileName = parent_folder+"/"+"wifitests_"+str(poll_delay)+"window"+window+"_libmapperdelay"+board+"_board.png"
    analysed_filename = parent_folder+"/"+"analysed_"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"

    # Name for simple moving average column
    smastr = 'SMA'+str(window)

    # check if analysed file already exists
    if os.path.exists(analysed_filename): # if I have already analysed it just open the file again
        fileExists = True
    else:
        fileExists = False
    if not fileExists:
    # If I haven't already analysed the data and cleaned it do it now
        # Open test daya
        rxdf = pd.read_csv(fileName)

        # Plot data
        time = rxdf["Latency"]*1000 # convert latency to ms
        time_abs = rxdf["time"]
        msg = rxdf["msg"] # grab messages

        # Filter out 0s
        filter_msg = msg[msg>0]
        filter_time = time[msg>0]
        filter_time_abs = time_abs[msg>0]

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
        msg_list = filter_msg.to_list()
        dif_list = msgDif.to_list()
        time_abs_list = filter_time_abs.to_list()
        new_latency = []
        new_dif = []
        new_msg = []
        new_time = []
        idx = 1
        tmp = 0
        while idx < len(time_list):
            # Increment temperary value
            if not math.isnan(time_list[idx]):
                tmp += time_list[idx]
            if logicDif[idx]:
                new_latency.append(tmp) # add if consecutive
                new_dif.append(dif_list[idx])
                new_msg.append(msg_list[idx])
                new_time.append(time_abs_list[idx])
                tmp = 0
            # Increment index
            idx += 1  

        # Create new timedf
        timedf = pd.DataFrame({'Latency':new_latency,'msgdif':new_dif,'msg':new_msg,'time':new_time})
        timedf['time_idx'] = pd.to_timedelta(timedf['time'], unit='s')
        timedf.set_index('time_idx',inplace=True)

        # Compute rolling average
        # Create new tmp
        tmpdf = pd.DataFrame({'Latency':new_latency,'time':new_time})
        tmpdf['time'] = pd.to_timedelta(tmpdf['time'], unit='s')
        tmpdf.set_index('time',inplace=True)

        # Compute rolling average over window
        timedf[smastr] = tmpdf.rolling(window).mean()
        timedf[smastr].dropna(inplace=True)
    else:
        # Get old analysed data
        timedf = pd.read_csv(analysed_filename,index_col='time_idx',parse_dates=True)

        # Set up tmpdf
        tmpdf = timedf[['time','Latency']]
        tmpdf['time'] = pd.to_timedelta(tmpdf['time'], unit='s')
        tmpdf.set_index('time',inplace=True)

        # Compute rolling average over window
        timedf[smastr] = tmpdf.rolling(window).mean()
        timedf[smastr].dropna(inplace=True)


    # Get average and standard deviation
    avg = timedf['Latency'].mean()
    stdev = timedf['Latency'].std()
    avg_stdev = timedf[smastr].std()

    # Get places without consecutive messages
    # timedf['consecutive'] = logicDif

    # Get array as a difference from the mean
    timedf['deviation'] = timedf['Latency'] - avg
    timedf['std_deviation'] = timedf['deviation']/stdev
    timedf['avg_std_deviation'] = timedf[smastr]/avg_stdev

    # Create plot and axis labels
    fig, axs = plt.subplots(2)

    # Plot Time
    timedf.plot(ax=axs[0],x='time',y='Latency',label='Latency', figsize=(16,8))

    
    # Plot Time
    timedf.plot(ax=axs[1],x='time',y=smastr,label='Simple Moving Average, window = ' + window, figsize=(16,8))

    # # Plot Deviation
    # timedf[['std_deviation']].plot(ax=axs[2],label='Deviation', figsize=(16,8))

    # # Plot Deviation
    # timedf[['avg_std_deviation']].plot(ax=axs[3],label='Deviation', figsize=(16,8))

    # Plot parameters
    # Latency Plot parameters
    axs[0].set_ylabel('Latency (ms)')
    axs[1].set_ylabel('Latency (ms)')
    # # Deviation Plot parameters
    # axs[2].set_ylabel('Deviation from Mean (ms)')
    # axs[3].set_ylabel('Deviation from Mean (ms)')

    # Limit y axis to see variation a bit better
    ylim0 = np.ceil(avg + stdev*10)
    ylim1 = np.ceil(avg + stdev*3)
    axs[0].set_ylim(0,ylim0)
    axs[1].set_ylim(0,ylim1)

    # Figure parameters
    titlestr = 'Latency of ' + board + ', Poll delay = ' + str(poll_delay) + ', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2)) +' Test Duration = ' + dur 
    fig.suptitle(titlestr)

    # Save figure
    fig.savefig(pic_fileName)
    plt.close(fig)

    # save analysed data
    timedf.to_csv(analysed_filename)

    # Print some statistics about this Data Set
    if not fileExists:
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
    else:
        reliabilityStats = ""
        return timedf, reliabilityStats

# Set test parameters
poll_delay = [0]
boards = ['tinypico','sparkfun']
parentFolder = 'test'
window = "1s"
smastr = 'SMA'+str(window)
dur = '30 minutes'
plot_distribution = False

# Setup empty list
dataDf = []
relList = []
legendList = []

# Create axis object for deviation plot
fig, ax = plt.subplots()
xlim = 1e6
fig.suptitle('Latency (ms) for TinyPico and Sparkfun, window =' + window)

for board in boards:
    for delay in poll_delay:
        # Get time df from analysis
        tmpdf,tmpreliability = analyse_data(delay,board,parentFolder,dur=dur,window=window)
        dataDf.append(tmpdf)
        relList.append(tmpreliability)

        # Plot on axis
        avg = tmpdf['Latency'].mean()
        stdev = tmpdf['Latency'].std()
        legendstr = board + ', Poll delay = ' + str(delay) +', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2))
        legendList.append(legendstr)
        tmpdf.plot(ax=ax,x='time',y=smastr,label=legendstr, figsize=(16,8))

        # Plot distribution
        if plot_distribution:
            titlestr = 'Latency of ' + board + ', Poll delay = ' + str(delay) + ', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2))
            plot_filename = parentFolder+"/"+"wifitests_"+str(delay)+"_libmapperdelay"+board+"_board_distribution.png"
            sns.displot(tmpdf, x='Latency')
            fig = plt.gcf()
            fig.suptitle(titlestr)
            fig.savefig(plot_filename)
            plt.close(fig)

        # Get xlimit
        if len(tmpdf) < xlim:
            xlim = len(tmpdf)

# Show plot
# ax.set_xlim(0,xlim)
ax.legend(legendList)
ax.set_ylim(0,50)
ax.set_xlabel('time (seconds)')
ax.set_ylabel('Latency (ms)')
plt.show()
    







