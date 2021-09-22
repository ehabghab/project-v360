import numpy as np
import os
import sys
import subprocess
import shlex

def main():
    if len(sys.argv) < 2:
        print "Error: python encode.py <dir>"
        sys.exit(1)
    dir = sys.argv[1].replace("./","").replace("/","")
    size = sys.argv[1].split("_")
    frameWidth = 3840
    frameHeight = 1920
    widthTiles = 12
    heightTiles = 12
    heightRange = frameHeight/heightTiles
    widthRange = frameWidth/widthTiles
    try:
        os.mkdir(dir+"/encoded_payloadExtract/")
    except OSError as error:
        True#print "error"
    for i in range(0,heightTiles): #row
        for j in range(0,widthTiles):
            stHeightRange = heightRange*i
            enHeightRange = heightRange*(i+1)
            stWidthRange = widthRange*j
            enWidthRange = widthRange*(j+1)
            if i == heightTiles - 1:
                enHeightRange = frameHeight
            if j == widthTiles -1 :
                enWidthRange = frameWidth
            w = enWidthRange-stWidthRange
            h = enHeightRange-stHeightRange
            f = dir+"/encoded/"+str(i*12+(j+1))+".mp4"
            try:
                os.mkdir(dir+"/encoded_payloadExtract/"+str(i*12+(j+1)))
            except OSError as error:
                True#print "error"

            o =dir+"/encoded_payloadExtract/"+str(i*12+(j+1))
            command = ("ffmpeg -i "+f+" -f image2 -vcodec copy -bsf h264_mp4toannexb "+o+"/%d.h264")
            #print command
            process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)

            stdout, stderr = process.communicate()
            #print stderr




if __name__ == "__main__":
        main()
