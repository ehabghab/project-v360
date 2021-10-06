import numpy as np
import os
import sys
import subprocess

def main():

    files = os.listdir("YuvW24H18_1")
    for f in files:
        command = "cat YuvW24H18_1/"+f+" YuvW24H18_2/"+f+" YuvW24H18_3/"+f+" > YuvW24H18/"+f
        process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        stdout, stderr = process.communicate()




if __name__ == "__main__":
        main()
