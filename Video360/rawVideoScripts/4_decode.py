import numpy as np
import os
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print "Error: python encode.py <dir>"
        sys.exit(1)
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
    outdir = dir+"/../decoded"
    try:
        os.mkdir(outdir)
    except OSError as error:
        True
    for f in files:
        command = "ffmpeg -i "+ dir+"/"+f+" "+outdir+"/"+f.replace(".mp4",".yuv")
        print command
        process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        stdout, stderr = process.communicate()






if __name__ == "__main__":
        main()
