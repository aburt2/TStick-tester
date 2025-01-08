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

# Lists for scenarios and order
frequency_list = ['5Ghz', '2.4Ghz']
condition_list = ['multiple devices', 'single device']

for condition in scenario:
    if condition > 2:
        idx = condition - 3
    else:
        idx = condition - 1

    # Get data from file
    tmpdf = analyse_data(condition,parentFolder,dur=dur)
    dataDf.append(tmpdf)

    # Get x limit
    upper_xlim = tmpdf['Latency'].quantile(0.99)+1
    bin_xlim = max(bin_xlim, upper_xlim)

    # Plot latency distribution
    if plot_distribution:
        titlestr = 'Latency Distribution: ' + frequency_list[idx]
        plot_filename = parentFolder+"/"+"wifitests_"+str(condition)+"_latencydelay.png"
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
    fig_box, ax_box = plt.subplots()
    fig_hist, ax_hist = plt.subplots()

    # create empty boxplot
    boxDf = pd.DataFrame({'Latency' : [],'Frequency' : [], 'Condition' : []})

    for condition in scenario:
        # Get scenario string
        if condition > 2:
            idx = condition - 3
            scenario_str = frequency_list[idx]
            condition_str = condition_list[1]
        else:
            idx = condition - 1
            scenario_str = frequency_list[idx]
            condition_str = condition_list[0]
        
        # Get Dataframe
        tmpdf = dataDf[idx]

        # Get scenario string
        print("Frequency: " + scenario_str)
        print("Condition: " + condition_str)

        # Add why information
        tmpdf['Frequency'] = scenario_str
        tmpdf['Condition'] = condition_str
        boxDf = pd.concat([boxDf, tmpdf], axis=0, ignore_index=True)

        # Set the legend
        avg = tmpdf['Latency'].quantile()
        stdev = (tmpdf['Latency'].quantile(0.75) - tmpdf['Latency'].quantile(0.25))/2
        legendstr = scenario_str
        legendList.append(legendstr)

        # Plot latency distribution
        if plot_distribution:
            sns.histplot(tmpdf, x='Latency', bins=np.arange(0, bin_xlim, 0.1), ax=ax_hist)

    # Plot box plot
    print(boxDf)
    sns.boxplot(data=boxDf, x='Latency', y = 'Condition',orient='h', width=0.2, whis=(0, 99), hue="Frequency", ax=ax_box)
    

    # Show the graph
    titlestr = 'Latency Distribution'
    fig_hist.suptitle(titlestr)
    fig_box.suptitle(titlestr)
    
    # Setup axis properties for histogram
    ax_hist.legend(legendList)
    ax_hist.set_xlim(0,bin_xlim)
    ax_hist.set_xlabel("Latency (ms)")

    # Setup axis properties for box plot
    ax_box.legend(legendList)
    ax_box.set_xlim(0,bin_xlim)
    # ax_box.set_ylim(-0.5,1.5)
    ax_box.set_xlabel("Latency (ms)")
    fig_box.tight_layout()

    plt.show()





