import io
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import csv
import datetime

datadir = r'\Users\waggoner\Downloads'
file = io.open(r'%s\pmt_ch5_1200V_yukon_1_ALL.csv'%datadir)
lines = [None]*1
outputdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\outputdata.csv'

minheight = None    #Default = None
threshold = None    #Default = None
distance = None     #Default = None
prominence = 0.016   #Default = None
width = None        #Default = None
wlen = None         #Default = None
rel_height = 0.5    #Default = 0.5
plateau_size = None #Default = None

def extract_data(inputfile,cutlines): #Takes a csv file, inputfile, and an int representing the number of lines to cut, 
                                      #and returns a list of lists containing all channels within.
    lines = inputfile.readlines()[cutlines:]
    output = []
    
    for i in range(len(lines)):
        output.append([])
    
    for line in lines:
        cols = [j for j in line.split(',')]
        for i in range(len(cols)):
            output[i].append(float(cols[i]))
    return output



def integration(a):
    out = np.empty((1,0)).tolist()
    for i in range(len(a)):
        if i == 0:
            out[i] = 0
        else: 
            out.append(0.5*(time_channel[i]-time_channel[i-1])*(a[i-1]*a[i]))
    return out

def compile_peaks(a): #Takes a list of peak heights and returns a float that represents the loss
    output = 0
    for i in range(len(a)):
        output += a[i]
    return float(output)
    
def store_data_point(a,b): #Takes a file path and a list of data points, and appends the data points to the CSV file
    with open(a, 'a',newline='') as outputfile:
        csvwriter = csv.writer(outputfile)
        csvwriter.writerow(b)
        outputfile.close()

##Extract Data
channels = extract_data(file,17)

##Define Plots
fig, ax = plt.subplots(1,2,figsize=(9,5))

time_channel = channels[0]
process_channel = channels[1]

##Define Raw Data Subplot
fig.suptitle("PMT trace")
fig.supxlabel('time (s)')
fig.supylabel('signal (V)')
ax[0].plot(time_channel,process_channel,label='PMT Data')
#ax[0].plot(t[0],ch2[0],label='PMT Data')
#ax[0].plot(t[0],np.divide(ch3[0],10),label='Toroid Data')
ax[0].set_title('Raw')
ax[0].legend()

raw_max = 0
for i in range(len(process_channel)):
    if abs(process_channel[i]) > raw_max:
        raw_max = abs(process_channel[i])

##Process Data
base = process_channel[0]
for i in range(len(process_channel)-1):
    process_channel[i] -= base

process_channel = integration(process_channel)

processed_max = 0
for i in range(len(process_channel)):
    if abs(process_channel[i]) > processed_max:
        processed_max = abs(process_channel[i])

scale_factor = raw_max / processed_max

for i in range(len(process_channel)):
    process_channel[i] *= scale_factor



peak_x = []
peak_y = []
    

for i in range(1):
    (peak_indices, *a) = signal.find_peaks(process_channel, minheight, threshold, distance, prominence + ((i)*0.001), width, wlen, rel_height, plateau_size)
    
    for j in range(len(peak_indices)):
        peak_x.append(time_channel[peak_indices[j]])
        peak_y.append(process_channel[peak_indices[j]])
    
    ax[i+1].scatter(peak_x,peak_y,color = "orange")

store_data_point(outputdir, [datetime.datetime.now(), compile_peaks(peak_y)])






##Define Processed Plot
#ax[1].plot(t[0],ch1[0],label='800V')
ax[1].plot(time_channel,process_channel,label='PMT Data')
#ax[2].plot(t[0],process_channel,label='PMT Data')
#ax[3].plot(t[0],process_channel,label='PMT Data')
#ax[1].plot(t[0],np.divide(ch3[0],10),label='Toroid Data')
ax[1].set_title('Processed')
ax[1].legend()
#ax[0].set_ylim(-0.04,0.04)
#ax[1].set_ylim(-0.04,0.04)

plt.show()