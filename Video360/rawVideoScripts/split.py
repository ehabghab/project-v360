import numpy as np
import os
def main():
    video = open("video.yuv",'rb')
    #1920x960
    frameWidth = 3840
    frameHeight = 2160

    widthTiles = 24
    heightTiles = 18
    heightRange = frameHeight/heightTiles
    widthRange = frameWidth/widthTiles

    dir = "YuvW"+str(widthTiles)+"H"+str(heightTiles)
    try:
        os.mkdir(dir)
    except OSError as error:
        True
    print str(widthRange)+"x"+str(heightRange)
    files = {}
    for i in range(0,heightTiles):
        files[i]={}
        for j in range(0,widthTiles):
            files[i][j] = open(dir+"/r_"+str(i+1)+"_c_"+str(j+1)+".yuv","w")

    startFrame = 0
    endFrame = 724
    video.seek(frameWidth* frameHeight* 1.5 * startFrame,0)
    for frame in range(startFrame,endFrame+1):
        print "Splitting frame #"+str(frame)
        yVal = {}
        #Y values
        for r in range (0,frameHeight):
            yVal[r] = list()
            for c in range(0,frameWidth):
                byte = video.read(1)
                yVal[r].append(byte)



        uVal = {}
        for r in range (0,frameHeight/4):
            uVal[r] = list()
            for c in range(0,frameWidth):
                byte = video.read(1)
                uVal[r].append(byte)


        vVal = {}
        for r in range (0,frameHeight/4):
            vVal[r] = list()
            for c in range(0,frameWidth):
                byte = video.read(1)
                vVal[r].append(byte)


        #frameHeight = 1080
        #frameWidth = 1920
        yValues = {}
        uValues = {}
        vValues = {}
        for i in range(0,heightTiles): #row
            yValues[i] = {}
            uValues[i] = {}
            vValues[i] = {}

            for j in range(0,widthTiles): #cols
                yValues[i][j] = list()
                uValues[i][j] = list()
                vValues[i][j] = list()

                stHeightRange = heightRange*i
                enHeightRange = heightRange*(i+1)
                stWidthRange = widthRange*j
                enWidthRange = widthRange*(j+1)

                if i == heightTiles - 1:
                    enHeightRange = frameHeight
                if j == widthTiles -1 :
                    enWidthRange = frameWidth

                #subblock y values
                for ii in range(stHeightRange, enHeightRange):
                    for jj in range(stWidthRange,enWidthRange):
                        #print str(stHeightRange)+"-->"+str(enHeightRange)+", "+str(stWidthRange)+"-->"+str(enWidthRange)
                        yValues[i][j].append(yVal[ii][jj])
                #subblock u/v values.
                prev = -1
                for ii in range(stHeightRange, enHeightRange,2):
                    row = ii/4
                    for jj in range(stWidthRange,enWidthRange,2):
                        if prev == row:
                            col = (frameWidth/2) + (jj/2)
                        else:
                            col = jj/2
                        uValues[i][j].append(uVal[row][col])
                        vValues[i][j].append(vVal[row][col])

                    prev = row

        for i in yValues:
            for j in yValues[i]:
                    for x in yValues[i][j]:
                        files[i][j].write(x)
                    for x in uValues[i][j]:
                        files[i][j].write(x)
                    for x in vValues[i][j]:
                        files[i][j].write(x)


    # for every 4 rows of Y, you have 1 U row and 1 V.





if __name__ == "__main__":
        main()
