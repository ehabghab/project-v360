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
    res1 = open("vp_corr_per_frame_user_3.txt")
    yaw = []
    pitch = []
    frame_ids = []
    frame_id = 1
    for line in res1.readlines():
        data = line.split(',')
        frame_ids.append(frame_id)
        yaw.append(float(data[0]))
        pitch.append(float(data[1]))
        frame_id += 1

    yaw_diff = []
    pitch_diff = []

    for idx in range(1, len(yaw)):
        diff = yaw[idx] - yaw[idx - 1]
        if diff > 200:  #overlapp
            diff = abs(diff - 360)
        elif diff < -200:
            diff += 360
        yaw_diff.append(diff)

    plt.figure(figsize=(16, 3))
    plt.tight_layout()

    plt.plot(frame_ids[1:], yaw_diff, linewidth=2, color='dodgerblue')

    plt.xticks([0, 200, 400, 600, 800, 1000, 1200, 1400], size=12)
    plt.yticks(size=12)
    #plt.xticks(size=12)
    plt.title("User trace", size=16)
    #plt.title("static", size=16)

    #plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    #plt.ylabel('Frac. of frames', size=14)
    #plt.xlabel('rebuffering time (ms)', size=14)
    plt.xlabel("Frame id", size=14)
    plt.ylabel("Yaw corrdinate - diff(degree)", size=14)
    #plt.ylim(78, 142)
    #plt.xlim(-1,10)
    # plt.show()
    plt.savefig("move_user_diff.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
