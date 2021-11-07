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

    switch_frame = []
    join_time = 0
    frame_ids = []
    for frameId in sorted(stitch_time):
        stall_time = (stitch_time[frameId] - playing_time[frameId]) * 1e3
        if frameId == 1:
            join_time = stall_time
        else:
            diff_time.append(stall_time)
            frame_ids.append(frameId)
            if stall_time > 2:
                switch_frame.append(frameId)
    print(switch_frame)
    # print(join_time)
    # print(len(diff_time))
    # print(sorted(diff_time))
    #sorted_data = np.sort(diff_time)
    #yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)

    plt.figure(figsize=(16, 3))
    plt.tight_layout()

    #for i in range(26, 1476, 25):
    #    plt.axvline(i, linestyle='--', color='grey')

    #plt.plot(sorted_data, yvals, linewidth=2,
    #        color='dodgerblue')
    plt.plot(frame_ids, diff_time, linewidth=2, color='dodgerblue')

    #plt.xticks([0,200,400,520,600,800,1000,1040,1200,1400],[0,200,400,'M',600,800,1000,'M',1200,1400],size=12)
    plt.yticks(size=12)
    plt.xticks(size=12)
    #plt.title("two 10-degree moves @ (520 \& 1040)", size=16)
    #plt.title("user", size=16)

    #plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    #plt.ylabel('Frac. of frames', size=14)
    #plt.xlabel('rebuffering time (ms)', size=14)
    plt.xlabel("Frame id", size=14)
    plt.ylabel("rebuffering time (ms)", size=14)
    plt.ylim(-1, 70)
    #plt.xlim(-1,10)
    # plt.show()
    plt.savefig("res1_decoding_TS.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
