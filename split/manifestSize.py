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
    fi = open("quality_tile_sizes_new.txt", 'w')
    root_dir = "YuvW12H12_new"
    qualities = [1, 2]
    tileSizes = {}  # quality -> tile# -> chunk# -> size(bytes)
    for quality in qualities:
        tileSizes[quality] = {}
        tilesDirs = os.listdir(root_dir+"/"+str(quality)+"/")
        for tileDir in tilesDirs:
            if tileDir in ".DS_Store":
                continue
            tileSizes[quality][int(tileDir)] = {}
            tileChunks = os.listdir(root_dir+"/"+str(quality)+"/"+tileDir)
            for tile in tileChunks:
                if tile in ".DS_Store":
                    continue
                fsize = os.path.getsize(
                    root_dir+"/"+str(quality)+"/"+tileDir + "/" + tile)
                tileSizes[quality][int(tileDir)][int(
                    tile.split(".")[0])] = fsize

    for qd in sorted(tileSizes):
        for td in sorted(tileSizes[qd]):
            s = str(qd)+"_"+str(td)+":"
            for t in sorted(tileSizes[qd][td]):
                s += str(tileSizes[qd][td][t])+","
            fi.write(s[:-1]+"\n")


if __name__ == "__main__":
    main()
