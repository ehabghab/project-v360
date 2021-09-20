import math
import matplotlib.pyplot as plt
import numpy as np
from os import system as sys
import os

from numpy.core.fromnumeric import sort

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"]
})


def main():
    diff_time = []
    res1 = open("res_dec_YUV.txt")
    stitch_time = {}
    playing_time = {}
    for line in res1.readlines():
        if "===" in line or "---" in line:
            continue
        if "Stitching" in line:
            frame = int(line.split("F#")[1])
            time = line.split()[1]
            hrs = int(time.split(":")[0])
            mins = int(time.split(":")[1])
            secs = float(time.split(":")[2])
            stitch_time[frame] = hrs * 3600. + mins * 60. + secs
        if "Playing" in line:
            frame = int(line.split("Frame#")[1])
            time = line.split()[1]
            hrs = int(time.split(":")[0])
            mins = int(time.split(":")[1])
            secs = float(time.split(":")[2])
            playing_time[frame] = hrs * 3600. + mins * 60. + secs

    join_time = 0
    frame_ids = []
    for frameId in sorted(stitch_time):
        stall_time = (stitch_time[frameId] - playing_time[frameId]) * 1e3
        if frameId == 1:
            join_time = stall_time
        else:
            diff_time.append(stall_time)
            frame_ids.append(frameId)

    # print(join_time)
    # print(len(diff_time))
    # print(sorted(diff_time))
    sorted_data = np.sort(diff_time)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)

    plt.figure(figsize=(5, 3))
    plt.tight_layout()
    plt.plot(sorted_data, yvals, linewidth=2, color='dodgerblue')

    plt.xticks(size=12)
    plt.yticks([.98, .985, .99, .995, 1], [.98, '', .99, '', 1], size=12)

    #plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    plt.ylabel('Frac. of frames', size=14)
    plt.xlabel('rebuffering time (ms)', size=14)
    plt.ylim(.98, 1.002)
    #plt.xlim(-1,10)
    # plt.show()
    plt.savefig("rebuffering1_decoding.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
