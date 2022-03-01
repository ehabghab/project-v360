
import math
import matplotlib.pyplot as plt
import numpy as np
from os import system
import sys
import os

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times",
    "font.sans-serif": ["Times"]})


def main():

    if len(sys.argv) < 2:
        print(
            "ERROR: python frac_skipped_tiles_per_vp_cdf.py \
                <user_tiles_per_frame_1> <user_tiles_per_frame_2> <play_log_1> <play_log_2>")
        sys.exit(1)
    ground_truth_user = {}
    user_map = {}
    c = 0

    for fname in [sys.argv[1], sys.argv[2]]:
        print(fname)
        user_id = "uid = "+fname.split("user_")[1].replace(".txt", "")
        user_map[c] = user_id
        ground_truth_user[c] = {}
        for line in open(fname).readlines():
            data = line.split(":")
            frame = int(data[0])
            tiles = data[1].replace("[", "").replace("]\n", "").split(",")
            tiles_list = []
            for tile in tiles:
                tiles_list.append(int(tile))
            ground_truth_user[c][frame] = tiles_list
        c += 1

    missed_tiles = {}
    c = 0
    for i in range(3, len(sys.argv)):
        missed_tiles[c] = {}
        fname = sys.argv[i]
        for line in open(fname).readlines():
            if "frame id" in line:
                continue
            data = line.split()
            missed_tiles_list = data[3] if len(data) == 4 else None
            if missed_tiles_list != None:
                missed_tiles[c][int(data[0])] = [int(x)
                                                 for x in data[3].split(',')]
        c += 1

    c = 0
    fraction_missed = {}
    for fname in missed_tiles:
        fraction_missed[c] = []
        for frame in ground_truth_user[c]:
            if frame > 1475:
                break
            missed_tiles_in_frame = 0.
            total_tiles_in_frame = 0.
            for tile in ground_truth_user[c][frame]:
                if missed_tiles[fname].get(frame) is not None:
                    if tile in missed_tiles[fname][frame]:
                        missed_tiles_in_frame += 1
                total_tiles_in_frame += 1.

            if total_tiles_in_frame != 0:
                fraction_missed[c].append(
                    missed_tiles_in_frame*100./total_tiles_in_frame)
        c += 1

    #["Empty", "15KB", "37.5KB", "65.25KB", "INF"]
    wait = ["Utility", "Flare"]
    colors = ['dodgerblue', 'seagreen', 'darkred', 'm']
    styles = ['-', ':', '-.', '--', 'dotted']

    plt.figure(figsize=(4, 2))
    plt.tight_layout()
    plt.subplot(111)
    plt.grid(True)
    c = 0
    for user_c in fraction_missed:
        sorted_data = np.sort(fraction_missed[user_c])
        yvals = np.arange(len(sorted_data)) * 100. / \
            float(len(sorted_data) - 1)
        plt.plot(sorted_data, yvals, linewidth=2,
                 linestyle=styles[c], color=colors[c], label="exp"+str(c+1))
        c += 1
    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.xlim(-0.5)
    plt.ylim(75)
    plt.legend(loc='lower right', prop={'size': 10,
               'weight': 'bold'}, edgecolor="black")
    plt.ylabel('\% of frames', size=12)
    plt.xlabel('\% of missed tiles', size=12)
    plt.savefig("frac_skipped_tiles_per_vp_musers.png",
                format="png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
