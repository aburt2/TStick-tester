import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
import os

# Define some analysis functions
def compute_reliability(dif_array, min_packet):
    '''
    Compute the reliability given a list of message differences and the minimum number of missed packets to be considered a failure
    '''
    #Compute difference threshold
    threshold = (min_packet + 1) * 0.01
    
    logicDif = np.where(dif_array > 0, 1, 0)
    missedDif = np.where(dif_array<threshold,1,0)

    # Calculate number of received messages, and missed messages
    rxmsg = sum(logicDif)
    missedmsg = len(dif_array)-sum(missedDif)
    
    # Calculate Reliability for 1, 2 and 5 consecutive missed messages
    reliability = 1 - missedmsg/len(dif_array)
    
    return rxmsg, missedmsg, reliability

def analyse_packet_loss(data, window):
    '''
    Analyse the packet loss 
    '''    
    # Create empty list
    packet_loss = []
    min_idx = 0
    total_packets = len(data)
    idx = 0
    
    print('Analysing Reliability Data will take a while')
    while (min_idx < (total_packets - window)):
        min_idx = idx
        max_idx = idx + window
        if (max_idx > total_packets):
            max_idx = total_packets - 1
        tmp_data = data[min_idx:max_idx]
        tmp_rel = compute_reliability(tmp_data, 1)[2]
        tmp_loss = 100*(1 - tmp_rel)
        packet_loss.append(tmp_loss[0])
        idx += 1
    
    # Create panda dataframe
    rel_data = pd.DataFrame({'Packet Loss (%)':packet_loss})
    return rel_data

def analyse_data(poll_delay,board,parent_folder,dur='60 seconds',window="1s"):
    '''
    Do some basic analysis on the wifi data
    '''
    # Construct file names
    fileName = parent_folder+"/"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"
    pic_fileName = parent_folder+"/"+"wifitests_"+str(poll_delay)+"window"+window+"_libmapperdelay"+board+"_board.png"
    analysed_filename = parent_folder+"/"+"analysed_"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"
    reliability_filename = parent_folder+"/"+"reliability_"+"wifitests_"+str(poll_delay)+"_libmapperdelay"+board+"_board.csv"

    # Name for simple moving average column
    smastr = 'SMA'+str(window)

    # check if analysed file already exists
    if os.path.exists(analysed_filename): # if I have already analysed it just open the file again
        fileExists = True
    else:
        fileExists = False
    
    if os.path.exists(reliability_filename): # if I have already analysed it just open the file again
        reliabilityfileExists = True
    else:
        reliabilityfileExists = False
    
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

        # Compute latency taking into account missed messages
        time_list = filter_time.to_list()
        msg_list = filter_msg.to_list()
        dif_list = msgDif.to_list()
        time_abs_list = filter_time_abs.to_list()
        new_latency = []
        new_dif = []
        new_msg = []
        new_time = []
        rel_time = []
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
                rel_time.append(time_abs_list[idx] - time_abs_list[0])
                tmp = 0
            # Increment index
            idx += 1  

        # Create new timedf
        timedf = pd.DataFrame({'Latency':new_latency,'msgdif':new_dif,'msg':new_msg,'time':new_time, 'relative_time':rel_time})
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
        timedf = pd.read_csv(analysed_filename,parse_dates=True)
    
    # Calculate Reliability for 1, 2 and 5 consecutive missed messages
    msgDif = timedf[['msgdif']]
    rxmsg, missedmsg, reliability = compute_reliability(msgDif, 1)
    
    # Get more detailed reliability data
    if not reliabilityfileExists:
        rel_df = analyse_packet_loss(msgDif, 1000)
        rel_df.to_csv(reliability_filename)
    else:
        rel_df = pd.read_csv(reliability_filename)

    # Get average and standard deviation
    avg = timedf['Latency'].mean()
    stdev = timedf['Latency'].std()
    avg_stdev = timedf[smastr].std()
    
    # Generate title string
    titlestr = 'Latency of ' + board + ', Poll delay = ' + str(poll_delay) + ', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2)) +' Test Duration = ' + dur 

    # Get array as a difference from the mean
    timedf['deviation'] = timedf['Latency'] - avg
    timedf['std_deviation'] = timedf['deviation']/stdev
    timedf['avg_std_deviation'] = timedf[smastr]/avg_stdev

    # Create plot and axis labels
    fig, axs = plt.subplots(2)
    
    # Plot Time
    timedf.plot(ax=axs[0],x='relative_time',y='Latency',label='Latency', figsize=(16,8))
    # Plot Time
    timedf.plot(ax=axs[1],x='relative_time',y=smastr,label='Simple Moving Average, window = ' + window, figsize=(16,8))

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
    fig.suptitle(titlestr)

    # Save figure
    fig.savefig(pic_fileName)
    plt.close(fig)

    if not fileExists:
        # save analysed data
        timedf.to_csv(analysed_filename)

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
    print(latencystr)
    print(reliabilitystr)
    print(extremestr)
    print(loweststr)
    print(endstr)

    # Return the df
    return timedf, rel_df

# Set test parameters
poll_delay = [0]
boards = ['tinypico','sparkfun']
parentFolder = 'ESP32/badConditionsResults'
window = "1s"
smastr = 'SMA'+str(window)
dur = '5 minutes'
plot_distribution = True
plot_reliability = True

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
        tmpdf.plot(ax=ax,x='relative_time',y=smastr,label=legendstr, figsize=(16,8))

        # Plot latency distribution
        if plot_distribution:
            titlestr = 'Latency Distribution of ' + board
            plot_filename = parentFolder+"/"+"wifitests_"+str(delay)+"_libmapperdelay"+board+"_board_distribution.png"
            tmpax = sns.displot(tmpdf, x='Latency')
            tmpax.set_axis_labels("Latency (ms)")
            tmpax.set(xlim=(0,30))
            tmpfig = plt.gcf()
            tmpfig.suptitle(titlestr)
            tmpfig.savefig(plot_filename)
            plt.close(tmpfig)

        if plot_reliability:
            titlestr = 'Packet Loss Distribution of ' + board
            plot_filename = parentFolder+"/"+"wifitests_"+str(delay)+"_libmapperdelay"+board+"_packet_loss.png"
            tmpax = sns.displot(tmpreliability, x='Packet Loss (%)')

            # Show what the target loss is
            min_loss = 1
            p1 = plt.axvline(x=min_loss,color='#36802D')
            
            # Change Plot Title
            tmpfig = plt.gcf()
            tmpfig.suptitle(titlestr)
            tmpfig.savefig(plot_filename)
            plt.close(tmpfig)

        # Get xlimit
        if len(tmpdf) < xlim:
            xlim = len(tmpdf)

# Show plot
# ax.set_xlim(0,xlim)
ax.legend(legendList)
ax.set_ylim(0,10)
ax.set_xlabel('time (seconds)')
ax.set_ylabel('Latency (ms)')
plt.show()
    







