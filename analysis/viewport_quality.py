
import math
import matplotlib.pyplot as plt
import numpy as np
from os import system
import sys
import os


def main():

    ground_truth = {}
    for line in open("tiles_per_frame_user_3.txt").readlines():
        data = line.split(":")
        frame = int(data[0])
        tiles = data[1].replace("[", "").replace("]\n", "").split(",")
        tiles_list = []
        for tile in tiles:
            tiles_list.append(int(tile))
        ground_truth[frame] = tiles_list

    recv_logs = []
    for i in range(1, len(sys.argv)):
        recv_logs.append(sys.argv[i])

    recv_chunk_quality = {}
    for recv_log in recv_logs:
        recv_chunk_quality[recv_log] = {}
        for line in open(recv_log).readlines():
            if "chunk" in line:
                continue
            data = line.split()
            chunk_id = int(data[0])
            tile_id = int(data[1])
            quality = int(data[2])
            recv_chunk_quality[recv_log][str(
                chunk_id)+"_"+str(tile_id)] = quality

    vp_quality_avg = {}
    for recv_log in recv_chunk_quality:
        vp_quality_avg[recv_log] = []
        for frame in ground_truth:
            chunk_id = int(((frame-1) / 25)) + 1
            quality_sum = 0.
            total_tiles = 0.
            for tile in ground_truth[frame]:
                key = str(chunk_id)+"_"+str(tile)
                if recv_chunk_quality[recv_log].get(key) is None:
                    continue
                quality_sum += recv_chunk_quality[recv_log][key]
                total_tiles += 1.
            if total_tiles != 0:
                vp_quality_avg[recv_log].append(quality_sum/total_tiles)

    bw = [100, 100, 100, 100]
    delay = [0, 20, 40, 100]
    colors = ['black', 'dodgerblue', 'seagreen', 'darkred']
    styles = ['-', '-.', '--', ':']

    plt.figure(figsize=(5, 3))
    plt.tight_layout()
    c = 0
    for f in sorted(vp_quality_avg):
        print(f)
        label = str(bw[c])+"mbps_"+str(delay[c])+"ms"
        sorted_data = np.sort(vp_quality_avg[f])
        yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
        plt.plot(sorted_data, yvals, linewidth=2,
                 linestyle=styles[c], color=colors[c], label=label)
        c += 1

    plt.xticks(size=12)
    plt.yticks(size=12)

    plt.legend(loc='best', prop={'size': 10, 'weight': 'bold'})
    plt.ylabel('Frac. of viewport-frames', size=14)
    plt.xlabel('Avg quality', size=14)
    # plt.ylim(.93,1.01)
    # plt.xlim(-1,10)
    # plt.show()
    plt.savefig("viewport_quality.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
