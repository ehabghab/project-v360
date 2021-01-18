import numpy as np
import os
import sys
import subprocess
import shlex
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print "Error: python encode.py <dir1> .. <dirN>"
        sys.exit(1)
    dirs = list()
    for i in range(1,len(sys.argv)):
        dirs.append(sys.argv[i].replace("./","").replace("/",""))

    frameSizes = {} #key is frameNum, value is size

    for dir in dirs:
        kdir = int(dir.replace("Width","").split("_Height")[0])
        frameSizes[kdir] = {}
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

    colors = ['r','g','b']
    c = 0

    plt.figure(figsize=(8,6))
    plt.subplot(111)
    for dir in sorted(frameSizes):
        print dir
        listSize = list()
        listFrameId = list()
        for frameId in frameSizes[dir]:
            #if frameSizes[1][frameId] > frameSizes[12][frameId]:
                #print str(frameId)+": "+str(frameSizes[1][frameId])+"-->"+str(frameSizes[12][frameId])
                listSize.append(frameSizes[dir][frameId]/1000.)
                listFrameId.append(frameId)

        sorted_data = np.sort(listSize)
        yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
        print np.percentile(listSize,70)
        plt.plot(sorted_data,yvals,linewidth=3,label = str(dir)+"x"+str(dir))
        #plt.scatter(listFrameId,listSize,linewidth=3,label = str(dir)+"x"+str(dir),color = colors[c])
        c+=1
    #plt.title("vID:"+str(video)+" uID:"+str(uID)+" [width "+str(tileWidth)+" X height"+str(tileHeight)+"], chunk length "+str(chunkLength) +"ms")
    plt.xticks(fontweight="bold",size=14)
    plt.yticks([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1],fontweight="bold",size=14)
    plt.legend(loc='best',prop={'size': 14,'weight':'bold'})
    plt.xlabel('Size (KB)',fontweight="bold",size=14)
    plt.ylabel('Frame Id',fontweight="bold",size=14)
    plt.grid()
    plt.xlim(1000)
    plt.ylim(.96,1.001)#,1)
    #plt.show()
    plt.savefig("4.png",dpi=300)
    #plt.close()








if __name__ == "__main__":
        main()
