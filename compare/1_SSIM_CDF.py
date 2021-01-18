import numpy as np
import os
import sys
import subprocess
import shlex
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def main():
    if len(sys.argv) < 2:
        print "Error: python encode.py <file1> .. <fileN>"
        sys.exit(1)
    files = list()
    for i in range(1,len(sys.argv)):
        files.append(sys.argv[i])

    ssims = {}
    for f in files:
        size = int(f.split("_")[0][1:])
        ssims[size] = {}

        for line in open(f).readlines():
            if "frame" in line or "average" in line:
                continue
            data = line.split(',')
            ssims[size][int(data[0])+1] = float(data[1])

    ssimlists = {}
    framelists = {}
    for size in ssims:
        ssimlists[size] = list()
        framelists[size] = list()
        for frame in sorted(ssims[size]):
            ssimlists[size].append(ssims[size][frame])
            framelists[size].append(frame)


    colors = ['r','g','b']
    marker = ['v','*','o']
    c = 0
    plt.figure(figsize=(8,6))
    plt.subplot(111)
    for size in sorted(ssimlists):
        sorted_data = np.sort(ssimlists[size])
        yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)

        if size != 12:
            plt.plot(sorted_data,yvals,linewidth=3,label = str(size)+"x"+str(size),color = colors[c])
        else:
            plt.plot(sorted_data,yvals,linewidth=3,label = str(size)+"x"+str(size),color = colors[c])
        c +=1
    plt.legend(loc='best',prop={'size': 14,'weight':'bold'})
    plt.xticks(fontweight="bold",size=14)
    plt.yticks(fontweight="bold",size=14)
    plt.xlabel('SSIM',fontweight="bold",size=14)
    plt.ylabel('Fraction of frames',fontweight="bold",size=14)
    plt.grid(which='both')
    #plt.xlim(.98,1)
    plt.ylim(0,1.001)#,1)
    #plt.show()
    plt.savefig("pnsr_CDF.png",dpi=300)
    #plt.close()





if __name__ == "__main__":
        main()
