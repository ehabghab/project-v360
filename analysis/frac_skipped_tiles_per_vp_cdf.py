
import math
import matplotlib.pyplot as plt
import numpy as np
from os import system
import sys
import os

# plt.rcParams.update({
#    "text.usetex": True,
#    "font.family": "sans-serif",
#    "font.sans-serif": ["Helvetica"]})


def main():

    if len(sys.argv) < 2:
        print(
            "ERROR: python frac_skipped_tiles_per_vp_cdf.py \
                <user_tiles_per_frame> <play_log_1> <play_log_2> .. <play_log_n>")
        sys.exit(1)
    ground_truth = {}
    for line in open(sys.argv[1]).readlines():
        data = line.split(":")
        frame = int(data[0])
        tiles = data[1].replace("[", "").replace("]\n", "").split(",")
        tiles_list = []
        for tile in tiles:
            tiles_list.append(int(tile))
        ground_truth[frame] = tiles_list

    missed_tiles = {}
    for i in range(2, len(sys.argv)):
        fname = sys.argv[i]
        missed_tiles[fname] = {}
        for line in open(fname).readlines():
            if "frame id" in line:
                continue
            data = line.split()
            missed_tiles_list = data[3] if len(data) == 4 else None
            if missed_tiles_list != None:
                missed_tiles[fname][int(data[0])] = [int(x)
                                                     for x in data[3].split(',')]

    fraction_missed = {}
    for fname in missed_tiles:
        fraction_missed[fname] = []
        for frame in ground_truth:
            if frame > 1475:
                break
            missed_tiles_in_frame = 0.
            total_tiles_in_frame = 0.
            for tile in ground_truth[frame]:
                if missed_tiles[fname].get(frame) is not None:
                    if tile in missed_tiles[fname][frame]:
                        missed_tiles_in_frame += 1
                total_tiles_in_frame += 1.

            if total_tiles_in_frame != 0:
                fraction_missed[fname].append(
                    missed_tiles_in_frame/total_tiles_in_frame)

    wait = [0, 30, 75, 112.5]  # [0, 15, 37.5, 65.25, 75]
    colors = ['black', 'dodgerblue', 'seagreen', 'darkred']
    styles = ['-', '-.', '--', ':']

    plt.figure(figsize=(5, 3))
    plt.tight_layout()
    plt.subplot(111)
    plt.grid(True)
    c = 0
    for fname in sorted(fraction_missed):
        sorted_data = np.sort(fraction_missed[fname])
        yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
        plt.plot(sorted_data, yvals, linewidth=2,
                 linestyle=styles[c], color=colors[c], label=str(wait[c])+"KB")
        c += 1
    plt.xticks(size=12)
    plt.yticks(size=12)
    plt.xlim(0, .1)
    plt.ylim(.9, 1)
    plt.legend(loc='best', prop={'size': 10, 'weight': 'bold'})
    plt.ylabel('Fraction of frames', size=14)
    plt.xlabel('Fraction of missed tiles in frame', size=14)
    plt.savefig("frac_skipped_tiles_per_vp.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
