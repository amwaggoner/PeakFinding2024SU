import io
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

datadir = r'\Users\waggoner\Downloads'
files = [io.open(r'%s\pmt_ch5_1200V_yukon_1_ALL.csv'%datadir)]
lines = [None]*len(files)

minheight = None    #Default = None
threshold = None    #Default = None
distance = None     #Default = None
prominence = 0.016   #Default = None
width = None        #Default = None
wlen = None         #Default = None
rel_height = 0.5    #Default = 0.5
plateau_size = None #Default = None

t = np.empty((1,0)).tolist()
ch1 = np.empty((1,0)).tolist()
ch2 = np.empty((1,0)).tolist()
ch3 = np.empty((1,0)).tolist()
ch4 = np.empty((1,0)).tolist()
ch2_1 = np.empty((1,0)).tolist()

def integration(a):
    out = np.empty((1,0)).tolist()
    for i in range(len(a)):
        if i == 0:
            out[i] = 0
        else: 
            out.append(0.5*(t[0][i]-t[0][i-1])*(a[i-1]*a[i]))
    return out


##Extract Data
for i in range(0,len(files)):
    lines[i] = files[i].readlines()[17:]
    
    for line in lines[i]:
        cols = [j for j in line.split(',')]
        t[i].append(float(cols[0]))    #timestamp
        ch1[i].append(float(cols[1]))  #scope ch 1
        ch2[i].append(float(cols[2]))  #pmt data
        #ch3[i].append(float(cols[3]))  #Toroid
        if len(cols)>4:
            ch4[i].append(float(cols[4]))
        else:
            ch4[i].append(0)

##Define Plots
fig, ax = plt.subplots(1,2,figsize=(9,5))

process_channel = ch1[0]

##Define Raw Data Subplot
fig.suptitle("PMT trace")
fig.supxlabel('time (s)')
fig.supylabel('signal (V)')
ax[0].plot(t[0],process_channel,label='PMT Data')
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
        peak_x.append(t[0][peak_indices[j]])
        peak_y.append(process_channel[peak_indices[j]])
    
    ax[i+1].scatter(peak_x,peak_y,color = "orange")

##Define Processed Plot
#ax[1].plot(t[0],ch1[0],label='800V')
ax[1].plot(t[0],process_channel,label='PMT Data')
#ax[2].plot(t[0],process_channel,label='PMT Data')
#ax[3].plot(t[0],process_channel,label='PMT Data')
#ax[1].plot(t[0],np.divide(ch3[0],10),label='Toroid Data')
ax[1].set_title('Processed')
ax[1].legend()
#ax[0].set_ylim(-0.04,0.04)
#ax[1].set_ylim(-0.04,0.04)

plt.show()