import csv
import io
import matplotlib.pyplot as plt


def extractdata(inputfile, cutlines):
    file = io.open(inputfile)
    lines = file.readlines()[cutlines:]
    output = []
    for i in lines:
        held = i.split(',')
        #print(type(held[0]))
        
        for j in held:
            j.replace(r'\n','')
            j.replace(r'[','')
            j.replace(r']','')
            j.replace("'",'')
        output.append(held)
    #print(len(output))
    return list(output)
    
def organizerawdata(inputdata):
    output = []
    for i in range(int(len(inputdata)/3)):
        held = []
        for j in range(3):
            held.append(inputdata[(i*3) + j])
        output.append(held)
        #print(len(output))
    
    return output
    
def plotdata(xaxis,yaxis):
    floatxaxis = []
    for i in xaxis:
        floatxaxis.append(float(i))
    
    floatyaxis = []
    for i in yaxis:
        floatyaxis.append(float(i))
        
      
    fig, ax = plt.subplots(1,2,figsize=(9,5))
    
    fig.suptitle("PMT trace")
    fig.supxlabel('time (s)')
    fig.supylabel('signal (V)')
    ax[0].scatter(floatxaxis,floatyaxis,label='PMT Data')
    ax[0].set_title('Raw')
    ax[0].legend()
    plt.show()