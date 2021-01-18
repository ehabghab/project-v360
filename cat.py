import numpy as np
import os
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print "Error: python cat.py <dir>"
        sys.exit(1)
    dir = sys.argv[1].replace("./","").replace("/","")
    frameWidth = 3840
    frameHeight = 2160

    files = os.listdir(dir)
    command = "cat "
    for i in range(1, len(files)+1):
        command += " Yuv/"+str(i)+".yuv"
    command += " > video.yuv"

    #command = "ffmpeg -f rawvideo -pix_fmt yuv420p -s:v "+str(w)+"x"+str(h)+" -r 25 -i "+f +" -g 5 -crf 24 -c:v libx264 "+o
    print command
    process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    stdout, stderr = process.communicate()





if __name__ == "__main__":
        main()
