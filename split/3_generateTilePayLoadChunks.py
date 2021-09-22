import numpy as np
import os
import sys
import subprocess
import shlex

def main():
    if len(sys.argv) < 2:
        print("Error: python encode.py <dir>")
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
        os.mkdir(dir+"/encoded_payloadExtractChunks/")
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

            out = dir+"/encoded_payloadExtractChunks/"+str(i*12+(j+1))
            try:
                os.mkdir(out)
            except:
                True
            inp = dir+"/encoded_payloadExtract/"+str(i*12+(j+1))
            ii = 0
            c = 1
            fis = ""
            for idx in range(1,1501):
                if (ii) % 25 == 0 and ii != 0:
                    command = ("cat "+fis+" > "+out+"/"+str(c)+".h264")
                    process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                    stdout, stderr = process.communicate()
                    ii = 0
                    c+=1
                
                    fis = ""
                fis += inp+"/"+str(idx)+".h264 "
                ii += 1
            
            
            #command = ("ffmpeg -i "+f+" -f image2 -vcodec copy -bsf h264_mp4toannexb "+o+"/%d.h264")
            #print command
            #process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)

            #stdout, stderr = process.communicate()
            #print stderr




if __name__ == "__main__":
        main()
