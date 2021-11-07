import numpy as np
import os
import sys
import subprocess
import shlex
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def main():
    if len(sys.argv) < 2:
        print "Error: python encode.py <dir1> .. <dirN>"
        sys.exit(1)
    dirs = list()
    for i in range(1,len(sys.argv)):
        dirs.append(sys.argv[i].replace("./","").replace("/",""))

    frameSizes = {}
    frameTypeI = {}
    frameTypeP = {}
    frameTypeB = {}
    for dir in dirs:
        kdir = int(dir.replace("Width","").split("_Height")[0])
        size = dir.split("_")
        frameWidth = 3840
        frameHeight = 1920
        widthTiles = int(size[0].split("Width")[1])
        heightTiles = int(size[1].split("Height")[1])
        heightRange = frameHeight/heightTiles
        widthRange = frameWidth/widthTiles

        tileFrameSizes = {} #key1 = tile, key2 = frameNum, value size
        frameSizes[kdir] = {} #key is frameNum, value is size
        count = 1
        for i in range(0,heightTiles): #row
            for j in range(0,widthTiles):
                tileFrameSizes[count] = {} # new tile
                dirTile = dir+"/EXP4/encoded_payloadExtract/"+str(i+1)+"_c_"+str(j+1)
                fList = os.listdir(dirTile)
                for f in fList:
                    frameNum = int(f.split(".")[0])
                    tileFrameSize = os.path.getsize(dirTile+"/"+f)
                    tileFrameSizes[count][frameNum] = tileFrameSize
                    if frameSizes[kdir].get(frameNum,None)==None:
                        frameSizes[kdir][frameNum] = 0
                    frameSizes[kdir][frameNum] += tileFrameSize
                count +=1




    colors = ['magenta','r','g','b']
    c = 0
    styles = ['-','--','.','-.']
    plt.figure(figsize=(8,6))
    plt.subplot(111)
    for dir in sorted(frameSizes):
        print dir
        print len(frameSizes[dir])
        print "====="
        listSize = list()
        listFrameId = list()
        for frameId in frameSizes[dir]:
            listSize.append((frameSizes[dir][frameId])/1000.)
            listFrameId.append(frameId)
        sorted_data = np.sort(listSize)
        yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
        if dir == 24:
            plt.plot(sorted_data,yvals,linewidth=3,label = str(dir)+"x"+str(18),color = colors[c])
        else:
            plt.plot(sorted_data,yvals,linewidth=3,label = str(dir)+"x"+str(dir),color = colors[c])
        c+=1
    plt.xticks(fontweight="bold",size=14)
    plt.yticks([0,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85,.9,.95,1]
               ,[0,'',.1,'',.2,'',.3,'',.4,'',.5,'',.6,'',.7,'',.8,'',.9,'',1]
               ,fontweight="bold",size=14)
    custom_lines = [
                Line2D([0], [0], linestyle='-',color='magenta', lw=4),
                Line2D([0], [0], linestyle='-',color='red', lw=4),
                Line2D([0], [0], linestyle='-',color='green', lw=4),
                Line2D([0], [0], linestyle='-',color='blue', lw=4)
                ]

    plt.legend(custom_lines,["1x1","6x6","12x12","24x18"],loc='best',prop={'size': 14,'weight':'bold'})
    plt.xlabel('Frame Size (KB)',fontweight="bold",size=14)
    plt.ylabel('fraction of frames',fontweight="bold",size=14)
    plt.title("ChunkLength 200ms",fontweight="bold",size=16)
    plt.grid(which='both')
    plt.xlim(300)
    plt.ylim(.8,1.01)#,1)
    #plt.show()
    plt.savefig("sizes_200_P2.png",dpi=300)
    #plt.close()








if __name__ == "__main__":
        main()
