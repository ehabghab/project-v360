

import re
import matplotlib.pyplot as plt
import numpy as np
import sys
import ast

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times",
    "font.sans-serif": ["Times"]})


def main():

    if len(sys.argv) < 2:
        print("Usage error: python3 viewport_quality_bg_fg.py play_log1 play_log2 ... play_logN ")
        sys.exit(1)

    # user trace --> list avg_quality for all vp frames
    avg_quality = {}
    for user_log_idx in range(1, len(sys.argv)):
        user_log = sys.argv[user_log_idx]
        avg_quality[user_log] = []
        for line in open(user_log, "r").readlines():
            if "frame" in line:
                continue
            data = line.split()
            if (len(data) == 4):  # skipped tiles or tiles quality is empty
                if "_" in data[3]:  # skipped tiles is empty
                    tiles_quality = data[3]
                    skipped_tiles = ""
                else:  # tile quality is empty
                    tiles_quality = ""
                    skipped_tiles = data[3]

            else:
                skipped_tiles = data[3]
                tiles_quality = data[4]

            if tiles_quality != "":
                tiles_quality_list = tiles_quality[:-1].split(",")
            else:
                tiles_quality_list = []

            if skipped_tiles != "":
                skipped_tiles_list = skipped_tiles[:-1].split(",")
            else:
                skipped_tiles_list = []

            quality_sum = 0.0
            tiles_count = len(skipped_tiles_list) + len(tiles_quality_list)
            for tile_quality in tiles_quality_list:
                quality_sum += int(tile_quality.split("_")[1])
            avg_quality[user_log].append(quality_sum*1.0/tiles_count)

    bw = [100, 100, 100, 100]
    delay = [0, 20, 40, 100]
    colors = ['dodgerblue', 'seagreen', 'darkred']
    styles = ['-', ':', '--']
    labels = ["Utility", "Flare-skip", "Flare-rebuffer"]

    plt.figure(figsize=(4, 2))
    ax = plt.subplot(111)
    c = 0
    for f in avg_quality:
        print(f)
        if "fg_5.5mbps_utility" in f:
            label = "fg\_utility"
        elif "flare" in f:
            label = "fg\_bg\_flare"
        else:
            label = "fg\_bg\_utility"

        print(f)
        print(np.percentile(avg_quality[f], 50))
        print(np.percentile(avg_quality[f], 90))
        sorted_data = np.sort(avg_quality[f])
        yvals = np.arange(len(sorted_data)) / \
            float(len(sorted_data) - 1)
        plt.plot(sorted_data, yvals, linewidth=2,
                 linestyle=styles[c], color=colors[c], label=label)
        c += 1
    plt.grid(color='dimgrey', linestyle=(0, (2, 4)), zorder=1)
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    plt.tick_params(axis='both', direction="in")
    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.legend(loc='upper left', ncol=1, prop={'size': 10,
               'weight': 'bold'}, edgecolor="black")
    plt.ylabel('\% of frames', size=12)
    plt.xlabel('Avg. quality', size=12)
    # plt.ylim(.93,1.01)
    plt.xlim(-0.1)
    # plt.show()
    plt.savefig("viewport_quality.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
