'''
Functions for plotting TPMs and calculating the score
'''
import matplotlib.pyplot as plt
import numpy as np

def plotTPM(tpmParams,plotParams):
    '''
    Plot the TPM graph based on the constraints and marginal value and scores
    Inputs:
        tpmParams: list containing TPM parameters
            constraints: list of constraints in ascending order
            marginal value: marginal value of the requirement
            scores: list of associated with the constraint and marginal value in the following order
                    [constraints[0] score, marginal value score, constraints[1] score]
        plotParams: list with the following plot parameters
                title: title string for the plot
                xlabel: xlabel string for plot
                ylabel: ylabel string for plot
                unit: Unit of the TPM measurement, if unitless put in N/A
    '''
    # Extract tpmParams
    constraints = tpmParams[0]
    marginal_value = tpmParams[1]
    scores = tpmParams[2]

    # Make x and y lists for ploting
    x = [constraints[0], marginal_value, constraints[1]]
    y = scores

    # Extract plot parameters
    title = plotParams[0]
    xlabel = plotParams[1]
    ylabel = plotParams[2]
    unit = plotParams[3]

    # Set plot parameters
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Set y limit between 0 and 1
    plt.ylim((0,1)) 
    plt.xlim(constraints)

    # Plot line
    plt.plot(x,y,'bo-')

    # Plot marker for Marginal value
    if unit == "N/A":  
        marg_string = "(" + str(marg_val) + ", " + str(scores[1]) + " score)"
    else:
        marg_string = "(" + str(marg_val) + unit + ", " + str(scores[1]) + " score)"
    arrowDict = dict(arrowstyle= '-|>',
                             color='black',
                             lw=3.5,
                             ls='--')
    plt.annotate(marg_string, (marg_val,scores[1]),textcoords="offset points",xytext=(0.5*marg_val,0),arrowprops=arrowDict)
    plt.show()

def scoreTPM(val,tpmParams):
    '''
    Calcuate the score the prototype got for this TPM given the tpm parameters
    Inputs:
        val: The meausred value the prototype achieved (ie: 200Hz control rate)
        tpmParams: list containing TPM parameters
            constraints: list of constraints in ascending order
            marginal value: marginal value of the requirement
            scores: list of associated with the constraint and marginal value in the following order
                    [constraints[0] score, marginal value score, constraints[1] score]
    '''
    # Extract tpmParams
    constraints = tpmParams[0]
    marginal_value = tpmParams[1]
    scores = tpmParams[2]

    # Check if value if below or above the constraints
    if (val <= constraints[0]):
        # If the value is below the low constraint return the low constraint score
        result = scores[0]
        return result
    elif (val >= constraints[1]):
        # if value is above the high constraint return the high constraint score
        result = scores[2]
        return result

    # Compute line slopes
    # m = (y2-y1)/(x2-x1)
    # m1 = (marg_val_score - low_constraint_score)/(marg_val - low_constraint)
    # m2 = (high_constraint score - marg_val_score)/(high_constraint - marg_val)
    m1 = (scores[1]-scores[0])/(marg_val -constraints[0])
    m2 = (scores[2]-scores[1])/(constraints[1]-marg_val)
    m = [m1,m2]
    print(m)

    # Find where score is on the line
    if (val <= marginal_value):
        line_idx = 0
    elif (val > marginal_value):
        line_idx = 1
    
    # Compute result
    # Linear interpolation formula
    # y = y0 + (val-x0)m
    x0 = marg_val
    y0 = scores[1]
    result = y0 + (val - x0)*m[line_idx]
    return result

if __name__ == "__main__":
    # tpm params
    marg_val = 200
    constraints = (100,1000)
    scores = [0,0.8,1]
    tpmParams = [constraints,marg_val,scores]

    # Plot Parameters
    title = "Requirement 1.1: Control Rate TPM"
    xlabel = "Frequency (Hz)"
    ylabel = "Score"
    unit = "Hz"
    plotParams = [title,xlabel,ylabel,unit]

    # Test score
    val = 150

    # Plot TPM
    result = scoreTPM(val,tpmParams)
    print(result)
    plotTPM(tpmParams, plotParams)