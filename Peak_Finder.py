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
    
def main():

    args_dict = {'readfile':'', 'event':'', 'dev_list':[],'role':''}
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
    
    print(nominals)
    
def dev_list():
    output = []
    for i in range(3999):
        output.append('L:PMT10W[%s]'%str(i))
    
    return output

def parse_args(args_dict):
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
    
def make_ramplist(sc,device_list):
    nominals = sc.get_settings_once(device_list)

    ramplist = []

    [ramplist.append(sum([[dev,float(nom)+i] for dev,nom in zip(device_list,nominals)],['1'])) for i in range(-3,4)]
    ramplist[0][0]='0'

    #print(ramplist)
    return ramplist
    
class scanner:
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
    
async def read_once(con,drf_list):

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
if __name__ == "__main__":
    main()