import csv
import io
import matplotlib.pyplot as plt

inputdir = r'\Users\waggoner\Documents\GitHub\PeakFinding2024SU\outputdata.csv'


def main():
    rawpoints = extractdata(inputdir,0)
    
    points = organizerawdata(rawpoints)
    
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    
    for i in range(len(points[0][1])):
        try: 
            x1.append(float(points[0][1][i]))
            y1.append(float(points[0][2][i]))
        except:
            print('ERROR: Non-numerical value. Skipping')
    
    for i in range(len(points[1][1])):
        try: 
            x2.append(float(points[1][1][i]))
            y2.append(float(points[1][2][i]))
        except:
            print('ERROR: Non-numerical value. Skipping')
    
    fig, ax = plt.subplots(1,2,figsize=(9,5))
    fig.suptitle("PMT trace")
    fig.supxlabel('time (s)')
    fig.supylabel('signal (V)')
    ax[0].scatter(x1,y1,label='PMT 2,3')
    ax[0].scatter(x2,y2,label='PMT 3,4')
    ax[0].set_title('Raw')
    ax[0].legend()
    plt.show()
    



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
    
    
    
if __name__ == "__main__":
    main()