import io
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import csv
import datetime
import acsys
import acsys.dpm
import acsys.sync
import aiostream
import asyncio
import logging
import argparse
import os
import time

'''

Notes for the user:
Files should be formatted as follows, with square brackets representing fields to be filled on data export

[Date in XX-XX-XXXX format]_[Voltage in XXXXV Format]_[Signal label in XX format]_DevList_[Underscore separated list of applicable device labels, such as filters or boards]_EndDevList_[Sample number in XXX format].csv


'''
#config files
lines = [None]*1
datadir = r'\Users\waggoner\Desktop\Data_Folder'
outputdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\outputdata.csv'
exampledir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\peak_example.csv'

#config peakfinding
minheight = None    #Default = None
threshold = None    #Default = None
distance = None     #Default = None
width = 0           #Default = None
wlen = None         #Default = None
rel_height = 0.5    #Default = 0.5
plateau_size = None #Default = None

channel_1_prominence_1 = 0.200  #Default = Nonechannel_1_prominence_1 = 0.200  #Default = None
channel_2_prominence_1 = 0.200  #Default = None
channel_1_prominence_2 = 0.200  #Default = None
channel_2_prominence_2 = 0.200  #Default = None
channel_1_prominence_3 = 0.200  #Default = None
channel_2_prominence_3 = 0.200  #Default = None

#config plotting
plot = False        #Does this need to be plotted? Default = False

#Config logging
FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)

#Initialize logging
log = logging.getLogger('acsys')
log.setLevel(logging.INFO)
log.info('script started')

#Attempt at implementing integration with digitizer. Requires work.
'''async def my_app(con):
    #devlist = dev_list()
    async with acsys.dpm.DPMContext(con) as dpmquery:
        log.info('adding entries')
        await dpmquery.add_entry(0, 'Z:CUBE_Z@i')
        
        log.info('starting dpm')
        await dpmquery.start()
        
        async for reply in dpmquery:
            log.info(str(reply.data))
    async for ii in acsys.sync.get_events(con, ['e,53']):
        log.info('%s',str(ii))'''
    
#Main, Entry point to the program
async def main():

    #Time Logging
    starttime = time.time()
    
    #Create variables for files and tasks(Tasks is a holdover from attempting to integrate digitizer)
    files = []
    tasks = []
    
    #Process every file in the data directory 
    for filename in os.listdir(datadir):
        run_script(datadir + r'\%s'%filename)
    
    #Log the time it took to complete processing of all files
    print('Entire script took ' + str(time.time() - starttime) + ' seconds to process ' + str(len(files)) + ' files')
    
    #Digitizer integration code. Requires work
    '''args_dict = {'readfile':'', 'event':'', 'dev_list':[],'role':''}
    parse_args(args_dict)
    
    sc = scanner()

    read_list = args_dict['dev_list'] + sc.readList(args_dict['readfile'])
    ramp_list = make_ramplist(sc,args_dict['dev_list'])
    #ramp_list=[]
    Nmeas = 1 # number of measurements to be taken at every setting
    
    devs = dev_list()
    nominals = sc.get_settings_once(devs)
    fig, ax = plt.subplots(1,2,figsize=(9,5))
    fig.suptitle("PMT trace")
    fig.supxlabel('time (s)')
    fig.supylabel('signal (V)')
    ax[0].plot(range(len(nominals)),nominals,label='PMT Data')
    ax[0].set_title('Raw')
    ax[0].legend()
    plt.show()
    
    print(nominals)'''
    
    
async def print_time(time): #Waits for an amount of time and passes how long it waited
    await asyncio.sleep(time)
    print(time)
    
    
def dev_list(): #Tinkering for the digitizer integration, ignore
    output = []
    for i in range(3999):
        output.append('L:PMT10W[%s]'%str(i))
    
    return output

def parse_args(args_dict): #Tinkering for the digitizer integration, ignore
    parser = argparse.ArgumentParser(description="usage: %prog [options] \n")
    parser.add_argument ('--readfile',  dest='readfile', default='Reading_devices.csv',
                         help="Reading device list file name. (default: Reading_devices.csv)")
    parser.add_argument ('--devlist',  dest='devlist', default=['L:QPS101'],
                         help="List of devices to scan. (default: Z:CUBE devices")
    parser.add_argument ('--event',  dest='event', default='@e,1d,e,0',
                         help="Event or periodic frequency. (default: '@p,1000')")
    parser.add_argument ('--role',  dest='role', default='testing',
                         help="Setting role. (default: 'testing')")
    
    
    options  = parser.parse_args()

    #assume files are in workdir
    args_dict['readfile'] = os.path.join(os.getcwd(),options.readfile)
    args_dict['event']    = options.event
    args_dict['dev_list'] = options.devlist
    args_dict['role']     = options.role
    
def run_script(inputfile): #Process the file's data to locate peaks
    #Log start time
    scriptstarttime = time.time()

    ##Extract Data
    file = io.open(inputfile)
    channels = extract_data(file,17)

    ##Define Plots
    if plot:
        fig, ax = plt.subplots(1,2,figsize=(9,5))

    ##Define channels
    time_channel = channels[0]
    process_channels = [channels[1],channels[2]]

    ##Define Raw Data Subplot
    if plot:
        fig.suptitle("PMT trace")
        fig.supxlabel('time (s)')
        fig.supylabel('signal (V)')
        ax[0].plot(time_channel,process_channels[0],label='PMT Data')
        ax[0].set_title('Raw')
        ax[0].legend()

    #Define the processed_channels variable
    processed_channels = []
    
    #Process all of the channels 
    for i in process_channels : 
        processed_channels.append(process_data(i,time_channel))

    
    #Plot the peaks found if configured to, but otherwise don't
    if plot:
        peak_finder(processed_channels, time_channel, inputfile, channels[3], ax)
    else:
        peak_finder(processed_channels, time_channel, inputfile, channels[3])

    ##Show the plot if configured to
    if plot:
        #ax[1].plot(time_channel,processed_channels[0],label='PMT Data')
        ax[1].set_title('Processed')
        ax[1].legend()

        plt.show()
    
    #Log the amount of time it took to process the file
    print('Processing one file took ' + str(time.time() - scriptstarttime) + ' seconds')

def extract_data(inputfile,cutlines): #Takes a csv file, inputfile, and an int representing the number of lines to cut, 
                                      #and returns a list of lists containing all channels within.
    #Log the time the data extraction started
    dataextractionstarttime = time.time()
    
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
                
    #Log the time it took to complete this step
    print('Extracting the data took ' + str(time.time() - dataextractionstarttime) + ' seconds')
    
    #Return the output
    return output



def integration(a, time_channel): #A function that reduces the noise of the wave form. Refactor code to rename this at some point.

    #Log the time this function started
    integrationstarttime = time.time()
    
    #Create an empty list
    out = np.empty((1,0)).tolist()
    
    #Log that the input is weird if the first, second, and third entries are all equal. 
    if a[0] == a[1] and a[1] == a[2]:
        print('input is weird')


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
                
    #Log the time it took to complete this step
    print('Applying the noise removal operation took ' + str(time.time() - integrationstarttime) + ' seconds')
    
    #Return noise reduced wave form
    return out


#Old peak processor
'''def compile_peaks(a): #Takes a list of peak heights and returns a float that represents the loss
    
    #Log the time this function started
    peakcompilationstarttime = time.time()
    
    #Define an output variable
    output = 0
    
    #Iterate over the entire list of peaks, adding all of
    for i in range(len(a)):
        output += a[i]
    
    print('Compiling the peaks took ' + str(time.time() - peakcompilationstarttime) + ' seconds')
    return float(output)'''
    
def store_data_point(a,b): #Takes a file path and a list of data points, and appends the data points to the CSV file
    #Log the time this function started
    datastoragestarttime = time.time()
    
    #open the csv file a and write b as a row into the file
    with open(a, 'a',newline='') as outputfile:
        csvwriter = csv.writer(outputfile)
        csvwriter.writerow(b)
        print('written line with length: ' + str(len(b)))
        outputfile.close()
        
    #Log the time it took to complete this step
    print('Storing the data took ' + str(time.time() - datastoragestarttime) + ' seconds')

def peak_finder(process_channels,time_channel, currentfile, toroid_channel, ax = None): #Takes a list of two input waveforms, a time channel, the file that the channel was retrieved from, the channel containing the toroid channel, and, if applicable, the plot to be drawn onto.
    #Log the time this function started
    peakfindingstarttime = time.time()
    
    #A variable to determine if the channel is the second channel
    second_channel = False
    
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
                
        '''for i in range(110000):
            splitinputs[0][0-i-1] = 0.0
        
        for i in range(110000):
            splitinputs[2][i] = 0.0'''
        
        #Purge the third list of the extra values that result from the extremely simple method of determining if the beam is present.
        for i in range(4500):
            splitinputs[2][i] = 0.0
        
        '''print(len(splittimes[0]))
        print(len(splittimes[1]))
        print(len(splittimes[2]))
        print(str(len(splittimes[0])+len(splittimes[1])+len(splittimes[2])))'''


        '''for i in splittimes[2]:
            if i < splittimes[1][-1]:
                splittimes[2].remove(i)
                splitinputs[2].remove(splitinputs[2][0])'''

        #Create the holding variables for the x and y coordinates of the peaks
        peak_x = []
        peak_y = []
        
        #Find peaks over each waveform.
        if second_channel:
            prominence = channel_1_prominence_1
        else:
            prominence = channel_2_prominence_1
        (peak_indices, *a) = signal.find_peaks(splitinputs[0], minheight, threshold, distance, prominence, width, wlen, rel_height, plateau_size)
        
        if second_channel:
            prominence = channel_1_prominence_2
        else:
            prominence = channel_2_prominence_2
        (peak_indices2, *a) = signal.find_peaks(splitinputs[1], minheight, threshold, distance, prominence, width, wlen, rel_height, plateau_size)
        
        if second_channel:
            prominence = channel_1_prominence_3
        else:
            prominence = channel_2_prominence_3 #0.200
        (peak_indices3, *a) = signal.find_peaks(splitinputs[2], minheight, threshold, distance, prominence, width, wlen, rel_height, plateau_size)
        
        #Define peak lists for each split portion of the channel
        peak_x_1 = []
        peak_y_1 = []
        peak_x_2 = []
        peak_y_2 = []
        peak_x_3 = []
        peak_y_3 = []

        #Iterate over each peak list and create an x and y value list for the peaks found
        for j in range(len(peak_indices)):
            peak_x_1.append(splittimes[0][peak_indices[j]])
            peak_y_1.append(splitinputs[0][peak_indices[j]])
            
        for j in range(len(peak_indices2)):
            peak_x_2.append(splittimes[1][peak_indices2[j]])
            peak_y_2.append(splitinputs[1][peak_indices2[j]])
            
        for j in range(len(peak_indices3)):
            peak_x_3.append(splittimes[2][peak_indices3[j]])
            peak_y_3.append(splitinputs[2][peak_indices3[j]])

        #Iterate over each x value list and append the x and y values to a combined list
        for j in range(len(peak_x_1)):
            peak_x.append(peak_x_1[j])
            peak_y.append(peak_y_1[j])
            
        for j in range(len(peak_x_2)):
            peak_x.append(peak_x_2[j])
            peak_y.append(peak_y_2[j])
            
        for j in range(len(peak_x_3)):
            peak_x.append(peak_x_3[j])
            peak_y.append(peak_y_3[j])

        #Plot the peaks if applicable
        if plot and second_channel: 
            '''and len(peak_x) < 2'''
            ax[1].plot(splittimes[0], splitinputs[0], color = "purple")
            ax[1].plot(splittimes[1], splitinputs[1], color = "pink")
            ax[1].plot(splittimes[2], splitinputs[2], color = "yellow")
            ax[1].scatter(peak_x_1,peak_y_1,color = "orange")
            ax[1].scatter(peak_x_2,peak_y_2,color = "red")
            ax[1].scatter(peak_x_3,peak_y_3,color = "green")

        #Define file information
        file_information = process_file_name(currentfile)
        
        '''print(len(peak_x))
        print(len(peak_y))'''

        #Store the results of this function
        store_data_point(outputdir, [datetime.datetime.now(), currentfile])
        store_data_point(outputdir,peak_x)
        store_data_point(outputdir,peak_y)

        #Set the second_channel variable to True
        second_channel = True
    
    #Log the time it took to complete this step
    print('Finding the peaks took ' + str(time.time() - peakfindingstarttime) + ' seconds')

def process_file_name(filename): #Returns a list of the file name split by _ characters, allowing information stored in the file name to be saved for other programs to use
    filename = filename.split(r'/')[-1]
    splitfilename = filename.split(r'_')
    return splitfilename
    #for i in range(len(splitfilename)):
        #return


def process_data(process_channel,time_channel): #Process the waveform provided to remove noise
    #Log the time this function started
    dataprocessingstarttime = time.time()
    
    #Define holding variable for the greatest value found in the raw data
    raw_max = 0
    
    #Find the greatest value found in the raw data
    for i in range(len(process_channel)):
        if abs(process_channel[i]) > raw_max:
            raw_max = abs(process_channel[i])
            
    ##Process Data    
    #Define the base value
    base = process_channel[0]
    
    #Iterate over the entire channel to be processed, subtracting the base from each value
    for i in range(len(process_channel)-1):
        process_channel[i] -= base
        
    #Apply the noise reduction function to the waveform
    process_channel = integration(process_channel,time_channel)
    #process_channel = integration(process_channel,time_channel)

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

    #Log the time it took to complete this step
    print('Finding the peaks took ' + str(time.time() - dataprocessingstarttime) + ' seconds')
    
    #Return processed channel waveform
    return process_channel
    
def make_ramplist(sc,device_list): #More stuff for Acsys integration attempt
    nominals = sc.get_settings_once(device_list)

    ramplist = []

    [ramplist.append(sum([[dev,float(nom)+i] for dev,nom in zip(device_list,nominals)],['1'])) for i in range(-3,4)]
    ramplist[0][0]='0'

    #print(ramplist)
    return ramplist
    
class scanner: #More stuff for Acsys integration attempt
    def __init__(self):
        self.thread_dict = {}
    
    def get_settings_once(self,paramlist):
        if paramlist and len(paramlist)!=0:
            drf_list = self.build_set_device_list(paramlist)
        else:
            print('Device list empty - abort')
            return
        nominals= acsys.run_client(read_once, drf_list=drf_list)
        return nominals
    def readList(self,filename):
        try:
            file = open(r'%s'%filename)
            lines = file.readlines()
            read_list = []
            for line in lines:
                if line.find('//') !=-1:
                    continue
                devs = [dev.strip('\n') for dev in line.split(',') if (dev.find(':')!=-1 or dev.find('_')!=-1) and isinstance(dev,str)] 
                [read_list.append(dev) for dev in devs]

        except:
            read_list = []
            print('Read device list empty')
        return read_list   
    def build_set_device_list(self,devlist):
        drf_list=[]
        for dev in devlist:
            drf = f'{dev}'
            drf_list.append(drf)
            
        return drf_list
    
async def read_once(con,drf_list): #More stuff for Acsys integration attempt

    settings = [None]*len(drf_list)
    async with acsys.dpm.DPMContext(con) as dpm:
        for i in range(len(drf_list)):
            await dpm.add_entry(i, drf_list[i]+'@i')

            await dpm.start()

        async for reply in dpm:
            settings[reply.tag]=reply.data
            #settings[reply.tag] = 1
            #print(reply.data)
            if settings.count(None) ==0:
                break
    return settings
    
log.info('running client')
'''acsys.run_client(my_app)'''
##run_script(hardcodefile)

#Start the program
if __name__ == "__main__":
    asyncio.run(main())