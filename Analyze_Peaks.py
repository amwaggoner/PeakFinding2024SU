import csv
import io
import matplotlib.pyplot as plt
import aiostream
import asyncio


peakdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\outputdata.csv'
outputdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\peak_analysis.csv'

def main():
    data = extractdata(peakdir,0)
    organizeddata = organizerawdata(data)
    
    algorithm_1(organizeddata)
    algorithm_2(organizeddata)
    
    #plotdata(organizeddata[0][1],organizeddata[0][2])
    #print(organizeddata[0][1])
    #print(organizeddata[0][2])

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

def store_data_point(a,b): #Takes a file path and a list of data points, and appends the data points to the CSV file
    with open(a, 'a',newline='') as outputfile:
        csvwriter = csv.writer(outputfile)
        csvwriter.writerow(b)
        outputfile.close()
        
def algorithm_1(inputs): #Takes an array of input arrays and produces an output based on the data provided. This algorithm just directly takes the sum of the data points.
    for i in inputs:
        store_data_point(outputdir, i[0])
        store_data_point(outputdir, ["algorithm 1"])
        heldvalue = 0.0
        for j in i[2]: 
            try:
                heldvalue += float(j)
            except:
                heldvalue += 0.0
            store_data_point(outputdir,[heldvalue])
            
def algorithm_2(inputs): #Takes an array of input arrays and produces an output based on the data provided. This algorithm takes the mean of the data points.
    for i in inputs:
        store_data_point(outputdir, i[0])
        store_data_point(outputdir, ["algorithm 2"])
        heldvalue = 0.0
        for j in i[2]: 
            try:
                heldvalue += float(j)
            except:
                heldvalue += 0.0
        heldvalue /= len(i[2])
        store_data_point(outputdir,[heldvalue])

def algorithm_3(inputs): #Takes an array of input arrays and produces an output based on the data provided. This algorithm 
    print('None')

if __name__ == "__main__":
    main()