import numpy as np
import os
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print "Error: python encode.py <dir>"
        sys.exit(1)
    dir = sys.argv[1].replace("./","").replace("/","")
    size = sys.argv[1].split("_")
    print size
    frameWidth = 3840
    frameHeight = 2160
    widthTiles = int(size[0].split("Width")[1])
    heightTiles = int(size[1].split("Height")[1])
    heightRange = frameHeight/heightTiles
    widthRange = frameWidth/widthTiles
    try:
        os.mkdir(dir+"/encoded")
    except OSError as error:
        True
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

            f = dir+"/raw_tiles/r_"+str(i+1)+"_c_"+str(j+1)+".yuv"
            o = dir+"/encoded/"+str(i+1)+"_c_"+str(j+1)+".mp4"

            #no B frames
            #command = "ffmpeg -f rawvideo -pix_fmt yuv420p -s:v "+str(w)+"x"+str(h)+" -r 25 -i "+f +" -g 5 -crf 24 -bf 0 -c:v libx264 "+o

            command = "ffmpeg -f rawvideo -pix_fmt yuv420p -s:v "+str(w)+"x"+str(h)+" -r 25 -i "+f +" -g 5 -crf 35 -c:v libx264 "+o

            process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
            stdout, stderr = process.communicate()





if __name__ == "__main__":
        main()
