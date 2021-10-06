import numpy as np
import os
import sys
def main():

    #The frame Width and height
    dir = sys.argv[1]
    files = os.listdir(dir)
    size = dir.split("/")[0].split("_")
    print size
    frameWidth = 3840
    frameHeight = 1920

    widthTiles = int(size[0].split("Width")[1])
    heightTiles = int(size[1].split("Height")[1])
    heightRange = frameHeight/heightTiles
    widthRange = frameWidth/widthTiles


    #In case we want to stitch some tiles
    #range [0, widthTiles-1]
    startCol = 0
    endCol = widthTiles-1
    #range [0, heightTiles-1]
    startRow = 0
    endRow = heightTiles-1

    #The output frame width and height
    frameHeight = heightRange * (endRow-startRow + 1)
    frameWidth = widthRange * (endCol-startCol + 1)
    print "Output Frame/Video Size (W:"+str(frameWidth)+" , H:"+str(frameHeight)+")"

    seekingBlockSize = frameWidth * frameHeight * 1.5
    startFrame = 0
    endFrame = 1500
    output = open(dir+"/../stitched_output.yuv",'w')
    files = {}
    for rx in range(startRow,endRow+1):
        files[rx] = {}
        for cx in range(startCol,endCol+1):
            files[rx][cx] = open(dir+"/"+str(rx+1)+"_c_"+str(cx+1)+".yuv",'r')
    for fnum in range(startFrame,endFrame):
        print "Stitching frame #"+str(fnum-startFrame)
        yVal = {}
        uVal = {}
        vVal = {}
        for rx in range(startRow,endRow+1):
            for cx in range(startCol,endCol+1):
                c = cx - startCol
                r = rx - startRow

                r = r * heightRange
                c = c * widthRange
                f = files[rx][cx]
                for i in range(r,r+heightRange):
                    if yVal.get(i,None) == None:
                        yVal[i] = {}
                    for j in range(c,c+widthRange):
                        yVal[i][j] = f.read(1)


                for i in range(r,r+heightRange,2):
                    row = i / 4
                    if uVal.get(row,None) == None:
                        uVal[row] = {}
                    for j in range(c,c+widthRange,2):
                        col = j / 2
                        if uVal[row].get(col,None) != None:
                            col = j / 2 + (frameWidth/2)
                        uVal[row][col] = f.read(1)

                for i in range(r,r+heightRange,2):
                    row = i / 4
                    if vVal.get(row,None) == None:
                        vVal[row] = {}
                    for j in range(c,c+widthRange,2):
                        col = j / 2
                        if vVal[row].get(col,None) != None:
                            col = j / 2 + (frameWidth/2)
                        vVal[row][col] = f.read(1)


        for i in range(0,len(yVal)):
            for j in range(0,len(yVal[i])):
                    output.write(yVal[i][j])

        for i in range(0,len(uVal)):
            for j in range(0,len(uVal[i])):
                output.write(uVal[i][j])


        for i in range(0,len(vVal)):
            for j in range(0,len(vVal[i])):
                    output.write(vVal[i][j])





if __name__ == "__main__":
        main()
