import io
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import csv
import datetime
import acsys
import acsys.dpm
import aiostream
import logging

datadir = r'\Users\waggoner\Downloads'
hardcodefile = r'%s\6-21-2024_1200V_Ev17_4_ALL.csv'%datadir
lines = [None]*1
outputdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\outputdata.csv'
exampledir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\peak_example.csv'

minheight = None    #Default = None
threshold = None    #Default = None
distance = None     #Default = None
prominence = 0.016   #Default = None
width = None        #Default = None
wlen = None         #Default = None
rel_height = 0.5    #Default = 0.5
plateau_size = None #Default = None
plot = True        #Does this need to be plotted? Default = False

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)

log = logging.getLogger('acsys')
log.setLevel(logging.INFO)
log.info('script started')

async def my_app(con):
    devlist = dev_list()
    async with acsys.dpm.DPMContext(con) as dpmquery:
        log.info('adding entries')
        await dpmquery.add_entries(list(enumerate(devlist)))
            
        log.info('starting queries')
        await dpmquery.start()
        
        async for ii in dpmquery.replies():
            print(str(ii))
    
    
def dev_list():
    output = []
    for i in range(1):
        output.append('L:PMT10W[{i}]')
    
    return output


def run_script(inputfile):
    ##Extract Data
    file = io.open(inputfile)
    channels = extract_data(file,17)

    ##Define Plots
    if plot:
        fig, ax = plt.subplots(1,2,figsize=(9,5))

    time_channel = channels[0]
    process_channel = channels[1]


    ##Define Raw Data Subplot
    if plot:
        fig.suptitle("PMT trace")
        fig.supxlabel('time (s)')
        fig.supylabel('signal (V)')
        ax[0].plot(time_channel,process_channel,label='PMT Data')
        ax[0].set_title('Raw')
        ax[0].legend()

    processed_channel = process_data(process_channel,time_channel)


    if plot:
        peak_finder(processed_channel, time_channel, ax)
    else:
        peak_finder(processed_channel, time_channel)

    ##Define Processed Plot
    if plot:
        ax[1].plot(time_channel,processed_channel,label='PMT Data')
        ax[1].set_title('Processed')
        ax[1].legend()

        plt.show()

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



def integration(a, time_channel):
    out = np.empty((1,0)).tolist()
    for i in range(len(a)):
        if i == 0:
            out[i] = 0.0
        else: 
            out.append(float(0.5*(time_channel[i]-time_channel[i-1])*(a[i-1]*a[i])))
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

def peak_finder(process_channel,time_channel, ax = None):
    peak_x = []
    peak_y = []
    

    for i in range(1):
        (peak_indices, *a) = signal.find_peaks(process_channel, minheight, threshold, distance, prominence + ((i)*0.001), width, wlen, rel_height, plateau_size)
    
        for j in range(len(peak_indices)):
            peak_x.append(time_channel[peak_indices[j]])
            peak_y.append(process_channel[peak_indices[j]])
    
        if plot:
            ax[i+1].scatter(peak_x,peak_y,color = "orange")

    store_data_point(outputdir, [datetime.datetime.now(), compile_peaks(peak_y)])


def process_data(process_channel,time_channel):
    
    raw_max = 0
    for i in range(len(process_channel)):
        if abs(process_channel[i]) > raw_max:
            raw_max = abs(process_channel[i])
    ##Process Data    
    
    base = process_channel[0]
    for i in range(len(process_channel)-1):
        process_channel[i] -= base
    process_channel = integration(process_channel,time_channel)


    processed_max = 0
    for i in range(len(process_channel)):
        if abs(process_channel[i]) > processed_max:
            processed_max = abs(process_channel[i])
    scale_factor = raw_max / processed_max
    if scale_factor == float('NaN'):
        print('There is an infinity in this data set')
    for i in range(len(process_channel)):
        process_channel[i] *= scale_factor

    return process_channel
    
log.info('running client')
acsys.run_client(my_app)
##run_script(hardcodefile)