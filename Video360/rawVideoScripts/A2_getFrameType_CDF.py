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

        kdir = int(dir.replace("YuvWidth","").split("_Height")[0])
        size = dir.split("_")
        frameWidth = 3840
        frameHeight = 2160
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
                dirTile = dir+"/encoded_payloadExtract/"+str(i+1)+"_c_"+str(j+1)
                fList = os.listdir(dirTile)
                for f in fList:
                    frameNum = int(f.split(".")[0])
                    tileFrameSize = os.path.getsize(dirTile+"/"+f)
                    tileFrameSizes[count][frameNum] = tileFrameSize
                    if frameSizes[kdir].get(frameNum,None)==None:
                        frameSizes[kdir][frameNum] = 0
                    frameSizes[kdir][frameNum] += tileFrameSize
                count +=1

        frameTypeI[kdir] = {} #key is frameNum, value is how many I
        frameTypeP[kdir] = {} #key is frameNum, value is how many P
        frameTypeB[kdir] = {} #key is frameNum, value is how many B
        for i in range(0,heightTiles): #row
            for j in range(0,widthTiles):
                fileTile = dir+"/encoded_type/"+str(i+1)+"_c_"+str(j+1)+".txt"

                frameNum = 1
                for line in open(fileTile,'r').readlines():
                    type = line.split("=")[1]
                    if frameTypeI[kdir].get(frameNum, None) == None:
                        frameTypeI[kdir][frameNum] = 0
                        frameTypeP[kdir][frameNum] = 0
                        frameTypeB[kdir][frameNum] = 0
                    frameTypeI[kdir][frameNum] = frameTypeI[kdir][frameNum]+1 if "I" in type else frameTypeI[kdir][frameNum]
                    frameTypeP[kdir][frameNum] = frameTypeP[kdir][frameNum]+1 if "P" in type else frameTypeP[kdir][frameNum]
                    frameTypeB[kdir][frameNum] = frameTypeB[kdir][frameNum]+1 if "B" in type else frameTypeB[kdir][frameNum]
                    frameNum +=1


    dicI = {}
    for dir in sorted(frameSizes):
        dicI[dir] = list()
        for frameId in sorted(frameTypeI[1]):
            if frameTypeI[1][frameId] == 1:
                dicI[dir].append(frameSizes[dir][frameId])

    dicP = {}
    for dir in sorted(frameSizes):
        dicP[dir] = list()
        for frameId in sorted(frameTypeP[1]):
            if frameTypeP[1][frameId] == 1:
                dicP[dir].append(frameSizes[dir][frameId])

    dicB = {}
    for dir in sorted(frameSizes):
        dicB[dir] = list()
        for frameId in sorted(frameTypeB[1]):
            if frameTypeB[1][frameId] == 1:
                dicB[dir].append(frameSizes[dir][frameId])


    for dir in dicI:
        print "====="
        print "scheme: "+str(dir)
        print "Avg size of I-frame: "+ str(sum(dicI[dir])/len(dicI[dir]))
        print "Avg size of P-frame: "+ str(sum(dicP[dir])/len(dicP[dir]))
        #print "Avg size of B-frame: "+ str(sum(dicB[dir])/len(dicB[dir]))

    colors = ['r','g','b']

    plt.figure(figsize=(8,6))
    plt.subplot(111)
    #I-Frame
    c = 0
    for dir in sorted(frameSizes):
        if 1 == dir:
            continue

        iC = 0
        iT = 0
        listSize = list()
        listFrameId = list()
        for frameId in sorted(frameTypeI[1]):
            if frameTypeI[1][frameId] == 1:
                listSize.append((frameSizes[dir][frameId]-frameSizes[1][frameId])/1000.)
                listFrameId.append(frameId)
                if frameSizes[dir][frameId] < frameSizes[1][frameId]:
                    iC+=1
                iT +=1
        print "======"
        print dir
        print str(iC)+"/"+str(iT)

        sorted_data = np.sort(listSize)
        yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
        plt.plot(sorted_data,yvals,linewidth=3,label = str(dir)+"x"+str(dir),color = colors[c])
        c+=1
    #P-frame
    c = 0
    for dir in sorted(frameSizes):
        if 1 == dir:
            continue
        pC = 0
        pT = 0
        listSize = list()
        listFrameId = list()
        for frameId in sorted(frameTypeP[1]):
            if frameTypeP[1][frameId] == 1:
                listSize.append((frameSizes[dir][frameId]-frameSizes[1][frameId])/1000.)
                listFrameId.append(frameId)
                if frameSizes[dir][frameId] < frameSizes[1][frameId]:
                    pC+=1
                pT +=1
        print "======"
        print dir
        print str(pC)+"/"+str(pT)

        sorted_data = np.sort(listSize)
        yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
        plt.plot(sorted_data,yvals,linewidth=3,label = str(dir)+"x"+str(dir),linestyle = '-.',color = colors[c])
        c+=1
    c = 0
    for dir in sorted(frameSizes):
        if 1 == dir:
            continue
        bC = 0
        bT = 0
        listSize = list()
        listFrameId = list()
        for frameId in sorted(frameTypeB[1]):
            if frameTypeB[1][frameId] == 1:
                listSize.append((frameSizes[dir][frameId]-frameSizes[1][frameId])/1000.)
                listFrameId.append(frameId)
                if frameSizes[dir][frameId] < frameSizes[1][frameId]:
                    bC+=1
                bT+=1
        print "======"
        print dir
        print str(bC)+"/"+str(bT)

        sorted_data = np.sort(listSize)
        yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
        plt.plot(sorted_data,yvals,linewidth=3,label = str(dir)+"x"+str(dir),linestyle = '--',color = colors[c])
        c+=1



    plt.xticks(fontweight="bold",size=14)
    plt.yticks([0,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85,.9,.95,1]
               ,[0,'',.1,'',.2,'',.3,'',.4,'',.5,'',.6,'',.7,'',.8,'',.9,'',1]
               ,fontweight="bold",size=14)


    custom_lines = [Line2D([0], [0], linestyle='-',color='black', lw=4),
                Line2D([0], [0], linestyle='-.',color='black', lw=4),
                Line2D([0], [0], linestyle='--',color='black', lw=4),
                Line2D([0], [0], linestyle='-',color='red', lw=4),
                Line2D([0], [0], linestyle='-',color='green', lw=4),
                Line2D([0], [0], linestyle='-',color='blue', lw=4)
                ]


    plt.legend(custom_lines,['I-frame','P-frame','B-frame',"6x6","12x12","24x18"],loc='best',prop={'size': 14,'weight':'bold'})
    plt.xlabel('Diff in Size (KB)',fontweight="bold",size=14)
    plt.ylabel('fraction of frames',fontweight="bold",size=14)
    plt.grid(which='both')
    #plt.xlim(-50,50)
    #plt.ylim(0,1.001)#,1)
    #plt.show()
    plt.savefig("FrameTypes.png",dpi=300)
    #plt.close()









if __name__ == "__main__":
        main()
