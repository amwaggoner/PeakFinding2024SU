import io
import os
import asyncio
import scipy.signal as signal
import numpy as np
import csv

'''

This script will print a range of prominence values which produce a configured range of peaks
Note that this does not account for peaks found outside of the beam pulse, as those contributions
are relatively minor relative to those found within the beam pulse.

'''

#Config section
datadir = r'\Users\waggoner\Desktop\Data_Folder'
outputdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\configinfo.csv'
minpeaks = 170         #Minimum number of peaks
maxpeaks = 190         #Maximum number of peaks
second_channel = False #Use the second channel?


#Peakfinding config section
minheight = None    #Default = None
threshold = None    #Default = None
distance = None     #Default = None
width = 0           #Default = None
wlen = None         #Default = None
rel_height = 0.5    #Default = 0.5
plateau_size = None #Default = None

prominenceranges = [[],[]]

#Main, Entry point to the program
async def main():

    
    #Create variables for files and tasks(Tasks is a holdover from attempting to integrate digitizer)
    files = []
    tasks = []
    
    #Process all files in the data directory 
    for filename in os.listdir(datadir):
        run_script(datadir + r'\%s'%filename)
        
    lowbar = np.mean(prominenceranges[0])
    highbar = np.mean(prominenceranges[1])
    
    print('The appropriate prominence values range from ' + str(lowbar)[:5] 
    + ' to ' + str(highbar)[:5])
    
def run_script(inputfile): #Process the file's data to locate peaks

    ##Extract Data
    file = io.open(inputfile)
    channels = extract_data(file,17)


    ##Define channels
    time_channel = channels[0]
    if(second_channel):
        process_channels = [channels[2]]
    else:
        process_channels = [channels[1]]


    #Define the processed_channels variable
    processed_channels = []
    
    #Process all of the channels 
    for i in process_channels : 
        processed_channels.append(process_data(i,time_channel))

    #Find Peaks
    peak_finder(processed_channels, time_channel, inputfile, channels[3])

def extract_data(inputfile,cutlines): #Takes a csv file, inputfile, and an int representing the number of lines to cut, 
                                      #and returns a list of lists containing all channels within.
    
    #Create a list, lines, and populate it with the lines of the input file, removing a number of lines equal to cutlines
    lines = inputfile.readlines()[cutlines:]
    
    #Define an output variable
    output = []
    
    #Create a number of empty lists equal to the length of the lines variable, and append them to output
    for i in range(len(lines)):
        output.append([])
    
    #Iterate over every element in the lines variable
    for line in lines:
        #Create a list containing the elements of the line
        cols = [j for j in line.split(',')]
        
        #Iterate over every index in the previously created list
        for i in range(len(cols)):
            
            #Append the value at that index to the output entry with that index, and otherwise append a None to that position
            try:
                output[i].append(float(cols[i]))
            except:
                print('ERROR: Non-numerical value found while extracting data. Skipping')
                output[i].append(None)
                
    #Return the output
    return output

def process_data(process_channel,time_channel): #Process the waveform provided to remove noise
   
    #Define the base value
    base = process_channel[0]
    
    #Iterate over the entire channel to be processed, subtracting the base from each value
    for i in range(len(process_channel)-1):
        process_channel[i] -= base
        
    #Apply the noise reduction function to the waveform
    process_channel = integration(process_channel,time_channel)

    #Define holding variable for the greatest value found in the raw data
    processed_max = 0
    
    #Find the greatest value found in the raw data
    for i in range(len(process_channel)):
        if abs(process_channel[i]) > processed_max:
            processed_max = abs(process_channel[i])
            
    #Find the scale factor 
    scale_factor = 1 / processed_max
    
    #Apply the scale factor to the processed waveform
    if scale_factor == float('NaN'):
        print('There is an infinity in this data set')
    for i in range(len(process_channel)):
        process_channel[i] *= scale_factor

    #Return processed channel waveform
    return process_channel
    
def integration(a, time_channel): #A function that reduces the noise of the wave form. Refactor code to rename this at some point.
    
    #Create an empty list
    out = np.empty((1,0)).tolist()

    #Iterate over the entire waveform
    for i in range(len(a)):
    
        #Set the first value in the output to 0.0
        if i == 0:
            out[i] = 0.0
            
        #Otherwise apply the noise reduction
        else: 
            try:
                in1 = float(a[i-1])
                in2 = float(a[i])
                out.append(float(0.5*(time_channel[i]-time_channel[i-1])*(in1*in2)))
            except:
                out.append(out[i-1])
                print("non-float found")
                

    #Return noise reduced wave form
    return out
    
def peak_finder(process_channels,time_channel, currentfile, toroid_channel, ax = None): #Takes a list of two input waveforms, a time channel, the file that the channel was retrieved from, the channel containing the toroid channel, and, if applicable, the plot to be drawn onto.
    
    #Iterate over both waveforms
    for i in process_channels: 
    
        #Define two holding channels. 
        inputchannel = []
        time_channel_processed = []
        
        #Iterate over the current waveform
        for j in range(len(i)):
            #Ensure that the entire waveform is composed of floats, removing values that are not valid floats
            try:
                inputchannel.append(float(i[j]))
                time_channel_processed.append(float(time_channel[j]))
            except:
                print('ERROR: Found non-numerical value. Skipping')

        #Define holding variables for the split waveform, as well as a variable defining if the beam has been found yet.
        splitinputs = [[],[],[]]
        splittimes = [[],[],[]]
        foundsignal = False
        
        #Iterate over the entire waveform
        for j in range(len(inputchannel)):
            #If the beam is present, place it in channel 2, but otherwise place it in channel 1 or 3 depending on if the beam has been found yet
            if toroid_channel[j] < 0.2:
                if foundsignal:
                    splitinputs[2].append(inputchannel[j])
                    splittimes[2].append(time_channel_processed[j])
                else:
                    splitinputs[0].append(inputchannel[j])
                    splittimes[0].append(time_channel_processed[j])
            else:
                splitinputs[1].append(inputchannel[j])
                splittimes[1].append(time_channel_processed[j])
                foundsignal = True
                
        
        #Purge the third list of the extra values that result from the extremely simple method of determining if the beam is present.
        for i in range(4500):
            splitinputs[2][i] = 0.0
        
        
        
        prominencerange = []
        
        #Find applicable prominence values
        for j in range(1000):
            prominence = j * 0.001
            (peak_indices, *a) = signal.find_peaks(splitinputs[1], minheight, threshold, distance, prominence, width, wlen, rel_height, plateau_size)
            if(len(peak_indices) > minpeaks and len(peak_indices) < maxpeaks):
                prominencerange.append(prominence)
        try:
            prominenceranges[0].append(prominencerange[0])
            prominenceranges[1].append(prominencerange[-1])
        except:
            print('There is no appropriate prominence range from 0.001 to 1.000 for this channel. Please confirm that the PMT was receiving power')


        

#Start the program
if __name__ == "__main__":
    asyncio.run(main())