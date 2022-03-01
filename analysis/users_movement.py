
import math
from re import L
import matplotlib.pyplot as plt
import numpy as np
from os import system as sys
import os
import sys

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times",
    "font.sans-serif": ["Times"]})


def modifybox(boxplot, data, whis=None, linewidth=None, color=None, medianColor=None, style=None):

    q1 = np.percentile(data, 10)
    q2 = np.percentile(data, 25)
    q3 = np.percentile(data, 50)
    q4 = np.percentile(data, 75)
    q5 = np.percentile(data, 90)
    if whis != None:
        q1 = np.percentile(data, whis[0])
        q5 = np.percentile(data, whis[1])

    boxplot['whiskers'][0].set_ydata([q1, q2])
    boxplot['caps'][0].set_ydata([q1, q1])
    # boxplot['boxes'][0].set_ydata([q2,q2,q4,q4,q2])
    boxplot['medians'][0].set_ydata([q3, q3])
    boxplot['caps'][1].set_ydata([q5, q5])
    boxplot['whiskers'][1].set_ydata([q4, q5])

    if linewidth == None:
        linewidth = 1

    if medianColor == None:
        medianColor = 'r'
    for cap in boxplot['caps']:
        cap.set(linewidth=linewidth, color=color)
    for cap in boxplot['boxes']:
        cap.set(linewidth=linewidth, hatch=style)
    for cap in boxplot['whiskers']:
        cap.set(linewidth=linewidth, color=color)
    for cap in boxplot['medians']:
        cap.set(linewidth=linewidth, color=medianColor)

    return q5


def main():

    if len(sys.argv) < 2:
        print("Error: Usage python3 users_movement.py <dir-vp-corrdinates>")
        sys.exit(1)

    files = os.listdir(sys.argv[1])
    vp_files = []
    for fi in files:
        if "vp" in fi:
            vp_files.append(fi)

    max_disp = {}
    median = {}
    for vp_file in vp_files:
        user_id = int(vp_file.split("vp_corr_per_frame_user_")
                      [1].replace(".txt", ""))
        frame = 0
        max_left = 0
        max_right = 0
        prev_yaw = -1
        for line in open(sys.argv[1]+"/"+vp_file, "r").readlines():

            yaw = float("%.2f" % float(line.replace("(", "").split(",")[0]))
            if prev_yaw != -1:
                if abs(prev_yaw - yaw) > 180:  # overlap case
                    if (prev_yaw < yaw):  # left
                        left_dis = (prev_yaw+360) - yaw
                        if left_dis > max_left:
                            max_left = left_dis
                    else:  # right
                        right_dis = (yaw+360) - prev_yaw
                        if right_dis > max_right:
                            max_right = right_dis
                else:
                    if (prev_yaw > yaw):  # left
                        left_dis = (prev_yaw) - yaw
                        if left_dis > max_left:
                            max_left = left_dis
                    else:  # right
                        right_dis = (yaw) - prev_yaw
                        if right_dis > max_right:
                            max_right = right_dis
            else:
                prev_yaw = yaw

            chunk_curr = int(frame / 25)
            frame += 1
            chunk_nex = int(frame / 25)
            if chunk_curr != chunk_nex:
                if max_disp.get(chunk_curr) is None:
                    max_disp[chunk_curr] = []
                max_disp[chunk_curr].append(
                    float("%.2f" % (max_left+max_right)))
                max_left = 0
                max_right = 0
                prev_yaw = yaw
        #median[user_id] = np.percentile(max_disp[user_id], 50)

    #user_idxs_median = []
    # for k, v in sorted(median.items(), key=lambda item: item[1]):
    #    user_idxs_median.append(k)

    plt.figure(figsize=(6, 3))
    ax = plt.subplot(111)
    boxprops = dict(linewidth=2, color="dodgerblue", facecolor='white')
    flierprops = dict(marker='x', markerfacecolor='k', markersize=2)

    user_id = 1
    for chunk in sorted(max_disp):
        boxplot = plt.boxplot(max_disp[chunk], showfliers=True, flierprops=flierprops, positions=[
                              user_id], widths=[.3], whis=[10, 90], boxprops=boxprops, patch_artist=True)
        modifybox(boxplot, max_disp[chunk], [
                  10, 90], 2, 'dodgerblue', 'k', '')
        user_id += 1
    ax.yaxis.set_ticks_position('both')

    plt.ylabel('Max displacement over 1-sec', size=12)
    plt.xlabel('chunk id', size=12)
    plt.xticks([i for i in range(0, 60, 5)], [
               i for i in range(0, 60, 5)], size=10)
    plt.yticks(size=10)

    plt.xlim(0)
    # plt.ylim(0,150)
    plt.savefig("user_movement_chunk.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
