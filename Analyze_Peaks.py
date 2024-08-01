import csv
import io
import matplotlib.pyplot as plt
import aiostream
import asyncio
import math


peakdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\outputdata.csv'
outputdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\peak_analysis.csv'



def main(): #Main Function, the Entry Point of the program
    data = extractdata(peakdir,0) #Extract the data from the outputdata.csv file described in peakdir
    organizeddata = organizerawdata(data) #Organize the data into a format used by the different methods in this file.
    
    #Apply each method to the data. 
    #algorithm_1(organizeddata)
    algorithm_2(organizeddata)
    #algorithm_3(organizeddata)
    #algorithm_4(organizeddata)
    
    #Plot the Results
    #plotdata(organizeddata[0][1],organizeddata[0][2])
    
    #print(organizeddata[0][1])
    #print(organizeddata[0][2])

def extractdata(inputfile, cutlines): #Extracts data from the inputfile(outputdata.csv) and returns it as a list of lists
    #Open the file
    file = io.open(inputfile)
    
    #Create a list of the lines in the file, excluding a number of lines equal to the cutlines parameter
    lines = file.readlines()[cutlines:]
    
    #Define the blank output list
    output = []
    
    #Iterate over each line
    for i in lines:
    
        #Split the line into its component entries
        held = i.split(',')
        
        #print(type(held[0]))
        
        #Remove special characters(Was found to be necessary)
        for j in held:
            j.replace(r'\n','')
            j.replace(r'[','')
            j.replace(r']','')
            j.replace("'",'')
            
        #Add the resulting list to the output list.
        output.append(held)
    #print(len(output))
    
    #Return a list of lists with the information contained within the file
    return list(output)

def organizerawdata(inputdata): #Organizes the data into a format the rest of the program can use
    #Define variable coontaining the return value
    output = []
    
    #Iterate over the list a number of times equal to a third the length of the list
    for i in range(int(len(inputdata)/3)):
        #Define variable temporarily holding a value
        held = []
        
        #Take the next three variables in the list and append them to the held variable
        for j in range(3):
            held.append(inputdata[(i*3) + j])
        
        #Append the resulting 3 term list to the output list
        output.append(held)
        #print(len(output))
    
    #return the list
    return output

def plotdata(xaxis,yaxis): #Plots the X and Y Axis passed as parameters on a scatter plot
    #Define a list which will hold the x axis
    floatxaxis = []
    
    #Iterates over the xaxis paramater and appends a cast float of each value to floatxaxis
    for i in xaxis:
        floatxaxis.append(float(i))
    
    #Define a list which will hold the y axis
    floatyaxis = []
    
    #Iterates over the yaxis paramater and appends a cast float of each value to floatyaxis
    for i in yaxis:
        floatyaxis.append(float(i))
        
    #Define plots  
    fig, ax = plt.subplots(1,2,figsize=(9,5))
    
    #Define the plot
    fig.suptitle("PMT trace")
    fig.supxlabel('time (s)')
    fig.supylabel('signal (V)')
    ax[0].scatter(floatxaxis,floatyaxis,label='PMT Data')
    ax[0].set_title('Raw')
    ax[0].legend()
    
    #Show the plot
    plt.show()

def store_data_point(a,b): #Takes a file path and a list of data points, and appends the data points to the CSV file
    #open the csv file a and write b as a row into the file
    with open(a, 'a',newline='') as outputfile:
        csvwriter = csv.writer(outputfile)
        csvwriter.writerow(b)
        outputfile.close()
        
def algorithm_1(inputs): #Takes an array of input arrays and produces an output based on the data provided. This algorithm just directly takes the sum of the data points.
    #Iterate over each array of data points provided in inputs
    for i in inputs:
    
        #Store the information relating to this data point
        store_data_point(outputdir, i[0])
        store_data_point(outputdir, ["algorithm 1"])
        
        #Define a holding variable
        heldvalue = 0.0
        
        #Iterate over the data in the list, adding values to the holding variable if possible
        for j in i[2]: 
            try:
                heldvalue += float(j)
            except:
                heldvalue += 0.0
        
        #Store the resulting sum in the output file
        store_data_point(outputdir,[heldvalue])
            
def algorithm_2(inputs): #Takes an array of input arrays and produces an output based on the data provided. This algorithm takes the mean of the data points.
    #Iterate over each array of data points provided in inputs
    for i in inputs:
    
        #Store the information relating to this data point
        store_data_point(outputdir, i[0])
        store_data_point(outputdir, ["algorithm 2"])
        
        #Define a holding variable
        heldvalue = 0.0
        
        #Iterate over the data in the list, adding values to the holding variable if possible
        for j in i[2]: 
            try:
                heldvalue += float(j)
            except:
                heldvalue += 0.0
        
        #Divide the holding variable by the length of the data set
        heldvalue /= len(i[2])
        
        #Store the resulting sum in the output file
        store_data_point(outputdir,[heldvalue])

def algorithm_3(inputs): #Takes an array of input arrays and produces an output based on the data provided. This algorithm normalizes the peaks then takes the mean of the values.
    #Iterate over each array of data points provided in inputs
    for i in inputs:
    
        #Define three holding variables, 1 array and 2 integers
        held1 = []
        held2 = 0
        held3 = 0
        
        #Iterate over the data in the list
        for j in i[2]:
            try:
                #Append e to the next value to the first holding variable
                held1.append(math.exp(float(j)))
                
                #Add the previous value to the second holding variable
                held2 += math.exp(float(j))
            except:
                print("Not a number, skipping")
    
        #Iterate over the contents of the first holding variable
        for j in held1:
        
            #Divide the value by the second holding variable
            j /= held2
            
            #Add the value to the third holding variable
            held3 += j

        #print(held3)

        #Define a variable normalizedinputs to be equal to the first holding variable
        normalizedinputs = held1

        try:
            #Confirm that the length of normalized inputs is not 0
            test = 1 /len(normalizedinputs)
            
            #Store the information relating to this data point
            store_data_point(outputdir, i[0])
            store_data_point(outputdir, ["algorithm 3"])
            
            #Set a holding variable to 0
            heldvalue = 0.0
            
            #Iterate over the values in normalizedinputs
            for j in normalizedinputs: 
                
                #Attempt to add the value to the holding variable, and add nothing if it fails
                try:
                    heldvalue += float(j)
                except:
                    heldvalue += 0.0
                    
            #Divide the holding variable by the length of normalizedinputs
            heldvalue /= len(normalizedinputs)
            
            #Store the resulting mean of softmaxes in the output file
            store_data_point(outputdir,[heldvalue])
        except:
            #On a failure of processing, store a value of 0.0 in the output file
            store_data_point(outputdir, i[0])
            store_data_point(outputdir, ["algorithm 3"])
            store_data_point(outputdir, [0.0])

def algorithm_4(inputs): #Takes an array of input arrays and produces an output based on the data provided.
    #Ramblings of tinkering. Ignore this as it appears to produce nothing different than Algorithm 3
    for i in inputs:
        held1 = []
        held2 = 0
        held3 = 0
        for j in i[2]:
            try:
                held1.append(math.exp(float(j)))
                held2 += math.exp(float(j))
            except:
                print("Not a number, skipping")
    
        for j in held1:
            j /= held2
            held3 += j

        #print(held3)

        normalizedinputs = held1
        heldvalue = 0.0
        for j in normalizedinputs: 
            try:
                heldvalue += float(j)
            except:
                heldvalue += 0.0
        try:
            heldvalue /= len(normalizedinputs)
        except:
            heldvalue = heldvalue
        
        heldvalue *= heldvalue
        
        heldvalue1 = 0.0
        for j in i[2]: 
            try:
                heldvalue1 += float(j)
            except:
                heldvalue1 += 0.0
        heldvalue1 /= len(i[2])
        
        heldvalue2 = heldvalue1 * heldvalue
        
        store_data_point(outputdir, i[0])
        store_data_point(outputdir, ["algorithm 4"])
        store_data_point(outputdir,[heldvalue2])
        
        
        
        
        '''store_data_point(outputdir, [0.0])'''

if __name__ == "__main__":
    main()