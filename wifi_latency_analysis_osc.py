import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
import os

def analyse_data(scenario,parent_folder,dur='100'):
    '''
    Do some basic analysis on the wifi data
    '''
    # Construct file names
    fileName = parent_folder+"/"+"wifitests_"+str(scenario)+"_latency.csv"
    analysed_filename = parent_folder+"/"+"analysed_"+"wifitests_"+str(scenario)+"_latency.csv"

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
        timedf = pd.read_csv(fileName)
    else:
        # Get old analysed data
        timedf = pd.read_csv(analysed_filename)

    # Get average and standard deviation
    avg = timedf['Latency'].quantile()
    stdev = (timedf['Latency'].quantile(0.75) - timedf['Latency'].quantile(0.25))/2

    # Generate title string
    titlestr = 'Latency of T-Stick, Scenario = ' + str(scenario) + ', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2)) +' Number of packets = ' + dur

    # Get array as a difference from the mean
    timedf['deviation'] = timedf['Latency'] - avg
    timedf['std_deviation'] = timedf['deviation']/stdev

    # Get percentage of values below the mean
    logicIdx = timedf['Latency'] <= avg
    per_below_mean = logicIdx.sum() / len(timedf['Latency'])

    if not fileExists:
        # save analysed data
        timedf.to_csv(analysed_filename)

    # Print some statistics about this Data Set
    # Set up strings
    startstr = '\n************************************************'
    endstr = '************************************************\n'
    latencystr = 'Average Latency = ' + str(avg) + u"\u00B1" + str(stdev) + 'ms'
    extremestr = 'Highest Latency = ' + str(max(timedf['Latency'])) + 'ms'
    loweststr = 'Lowest Latency = ' + str(min(timedf['Latency'])) + 'ms'
    highPercentilestr = 'Top 1%% Latency = ' + str(timedf['Latency'].quantile(0.01)) + 'ms'
    lowPercentilestr = 'Bottom 1%% Latency = ' + str(timedf['Latency'].quantile(0.99)) + 'ms'
    print(startstr)
    print(titlestr)
    print(latencystr)
    print(extremestr)
    print(loweststr)
    print(highPercentilestr)
    print(lowPercentilestr)
    print(endstr)

    # Return the df
    return timedf

# Set test parameters
scenario = [3,4]
parentFolder = 'data/enchantiW106'
window = "1s"
smastr = 'SMA'+str(window)
dur = '1000'
plot_distribution = True
plot_reliability = True

# Setup empty list
dataDf = []
relList = []
legendList = []
bin_xlim = 0

scenario_list = ['5Ghz multiple devices', '2.4Ghz multiple devices', '5GHz single device', '2.4GHz single device']


for delay in scenario:
    # Get time df from analysis
    print(delay)
    tmpdf = analyse_data(delay,parentFolder,dur=dur)
    dataDf.append(tmpdf)

    # Get x limit
    upper_xlim = tmpdf['Latency'].quantile(0.99)+1
    bin_xlim = max(bin_xlim, upper_xlim)

    # Plot latency distribution
    if plot_distribution:
        titlestr = 'Latency Distribution: ' + scenario_list[delay-1]
        plot_filename = parentFolder+"/"+"wifitests_"+str(delay)+"_latencydelay.png"
        tmpax = sns.displot(tmpdf, x='Latency')
        tmpax.set_axis_labels("Latency (ms)")
        tmpax.set(xlim=(0,upper_xlim))
        tmpfig = plt.gcf()
        tmpfig.suptitle(titlestr)
        tmpfig.savefig(plot_filename)
        plt.close(tmpfig)

# Create a combined graph

if len(scenario) > 1:
    # Create axis object for deviation plot
    fig, ax = plt.subplots()

    # compute max range of bins
    bin_xlim = int(np.ceil(bin_xlim))

    for idx in range(0, len(scenario)):
        # Get time df from analysis
        tmpdf = dataDf[idx]

        # Set the legend
        avg = tmpdf['Latency'].quantile()
        stdev = (tmpdf['Latency'].quantile(0.75) - tmpdf['Latency'].quantile(0.25))/2
        legendstr = scenario_list[scenario[idx]-1] +', Average = ' + str(np.round(avg,2)) + u"\u00B1" + str(np.round(stdev,2))
        legendList.append(legendstr)

        # Plot latency distribution
        if plot_distribution:
            sns.histplot(tmpdf, x='Latency', bins=np.arange(0, bin_xlim, 0.1), ax=ax)
    

    # Show the graph
    titlestr = 'Latency Distribution'
    print(legendList)
    ax.legend(legendList)
    ax.set_xlim(0,bin_xlim)
    ax.set_xlabel("Latency (ms)")
    fig.suptitle(titlestr)
    plt.show()





