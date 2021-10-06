import numpy as np
import os
import sys
import subprocess
import shlex
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"]})

def main():

    root_dir = "YuvW12H12"
    gops = [30,24,16,8,4,2,1]
    chunkSizes = {}
    tile_chunk_size = {}
    frame_size = {}
    c = 0
    for gop in gops:
        chunkSizes[gop] = {}
        tile_chunk_size[gop] = {}
        frame_size[gop] = {}
        subdirs = os.listdir(root_dir+"/gop"+str(gop)+"/encoded_payloadExtract")
        for subdir in subdirs:
            if "c_" not in subdir:
                continue
            subdir_files = os.listdir(root_dir+"/gop"+str(gop)+"/encoded_payloadExtract"+"/"+subdir)
            tile_chunk_size[gop][subdir] = {}
            for file in subdir_files:
                fsize = os.path.getsize(root_dir+"/gop"+str(gop)+"/encoded_payloadExtract"+"/"+subdir+"/"+file)
                fname = int(file.split(".")[0])
                chunk_id = (fname - 1) / gop
                if gop == 30 and (fname) <= 30:
                    c+= fsize
                if chunkSizes[gop].get(chunk_id) is None:
                    chunkSizes[gop][chunk_id] = 0
                if frame_size[gop].get(fname) is None:
                    frame_size[gop][fname] = 0
                if tile_chunk_size[gop][subdir].get(chunk_id) is None:
                    tile_chunk_size[gop][subdir][chunk_id] = 0
                tile_chunk_size[gop][subdir][chunk_id] += fsize
                chunkSizes[gop][chunk_id] += fsize
                frame_size[gop][fname] += fsize
    
    tile_chunk_size_summary = {}
    for gop in tile_chunk_size:
        tile_chunk_size_summary[gop] = []
        for subdir in tile_chunk_size[gop]:
            for chunk_id in tile_chunk_size[gop][subdir]:
                tile_chunk_size_summary[gop].append(tile_chunk_size[gop][subdir][chunk_id])

    print("Tile-chunk size")
    for gop in tile_chunk_size_summary:
        avg = sum(tile_chunk_size_summary[gop]) * 1. / len(tile_chunk_size_summary[gop])
        print(str(gop)+":"+str(avg/1000)+" KB")

    print("Frame size")
    for gop in frame_size:
        l = list()
        for chunk_id in frame_size[gop]:
            l.append(frame_size[gop][chunk_id])
        avg = sum(l) * 1. / len(l)
        print(str(gop)+":"+str(avg/1000)+" KB")
      

    x_axis = []
    y_axis = []
    for gop in sorted(chunkSizes):
        sum_size = 0.
        count = 0.
        for chunk_id in chunkSizes[gop]:
            sum_size += chunkSizes[gop][chunk_id] 
            count += 1
        avg = sum_size / count
        x_axis.append(gop)
        y_axis.append(avg/1000.)

    print(y_axis)
    
    plt.figure(figsize=(5,3))
    plt.subplot(111)
    plt.plot(x_axis,y_axis,linewidth=1.25,color='dodgerblue',marker='x')
    plt.xticks(x_axis,x_axis,fontweight="bold",size=14)
    plt.yticks(fontweight="bold",size=14)
    #plt.legend(loc='best',prop={'size': 14,'weight':'bold'})
    plt.ylabel('Chunk size (KB)',fontweight="bold",size=14)
    plt.xlabel('\# frames/chunk',fontweight="bold",size=14)
    plt.grid(True,linestyle=':')
    plt.ylim(0)
    plt.savefig("chunkSize.png",dpi=300,bbox_inches='tight', pad_inches=0.03)


if __name__ == "__main__":
        main()
