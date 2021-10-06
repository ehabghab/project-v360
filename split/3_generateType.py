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
    
    frameWidth = 3840
    frameHeight = 1920
    widthTiles = int(12)
    heightTiles = int(12)
    heightRange = frameHeight/heightTiles
    widthRange = frameWidth/widthTiles
    try:
        os.mkdir(dir+"/encoded_type/")
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
            o =dir+"/encoded_type/"+str(i*12+(j+1))+".txt"
            command = ("ffprobe "+f+" -show_frames | grep -E 'pict_type' > "+o)
            process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)

            stdout, stderr = process.communicate()
            #print stderr




if __name__ == "__main__":
        main()
