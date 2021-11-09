
import math
import matplotlib.pyplot as plt
import numpy as np
from os import system
import sys
import os


def main():

    if len(sys.argv) < 6:
        print(
            "ERROR: python QoE.py <user_tiles_per_frame> <usr_vp_corr> <recv_log> <play_log> <pred_log>")
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

    yaws = []
    pitches = []
    for line in open(sys.argv[2]).readlines():
        data = line.split(",")
        yaws.append(float(data[0]))
        pitches.append(float(data[1]))
    yaws = yaws[:-25]
    pitches = pitches[:-25]

    recv_chunk_quality = {}
    for line in open(sys.argv[3]).readlines():
        if "chunk" in line:
            continue
        data = line.split()
        chunk_id = int(data[0])
        tile_id = int(data[1])
        quality = int(data[2])
        recv_chunk_quality[str(
            chunk_id)+"_"+str(tile_id)] = quality

    vp_quality_avg = []
    for frame in ground_truth:
        chunk_id = int(((frame-1) / 25)) + 1
        quality_sum = 0.
        total_tiles = 0.
        for tile in ground_truth[frame]:
            key = str(chunk_id)+"_"+str(tile)
            if recv_chunk_quality.get(key) is None:
                continue
            quality_sum += recv_chunk_quality[key]
            total_tiles += 1.
        if total_tiles != 0:
            vp_quality_avg.append(quality_sum/total_tiles)

    rebuffer_time = [0]
    prev_render = -1
    for line in open(sys.argv[4]).readlines():
        if "frame id" in line:
            continue
        data = line.split()
        render_time = int(data[2])
        if prev_render != -1:
            rebuffer_time.append((render_time-prev_render)-40)
        prev_render = render_time

    yaw_pred_per_frame = {}  # key: frame, value: list of yaw predictions
    pitch_pred_per_frame = {}  # key: frame, value: list of pitch predictions
    for line in open(sys.argv[5]):
        True

    sys.exit(1)

    bw = [100, 100, 100, 100]
    delay = [0, 20, 40, 100]
    colors = ['black', 'dodgerblue', 'seagreen', 'darkred']
    styles = ['-', '-.', '--', ':']

    frame_ids = [i for i in range(1, 1476)]
    plt.figure(figsize=(16, 12))
    plt.tight_layout()
    plt.subplot(311)
    plt.plot(frame_ids, vp_quality_avg, linewidth=2,
             linestyle='-', color='dodgerblue')
    x_ticks = []
    x_ticks2 = []
    for i in range(1, 1476):
        if i % 25 == 0:
            x_ticks2.append(i)
            if i % 50 == 0:
                x_ticks.append('')
            else:
                x_ticks.append((i/25) + 1)
    plt.xticks(size=12)
    plt.yticks([0, 1, 2], ['None', 'LQ', 'HQ'], size=12)

    # plt.legend(loc='best', prop={'size': 10, 'weight': 'bold'})
    plt.ylabel('Viewport avg quality', size=14)
    plt.xlabel('Frame Id', size=14)

    plt.subplot(312)
    plt.plot(frame_ids, rebuffer_time, linewidth=2,
             linestyle='-', color='seagreen')
    plt.xticks(size=12)
    plt.yticks(size=12)

    # plt.legend(loc='best', prop={'size': 10, 'weight': 'bold'})
    plt.ylabel('Rebuffering (ms)', size=14)
    plt.xlabel('Frame Id', size=14)

    # plt.ylim(.93,1.01)
    # plt.xlim(-1,10)
    # plt.show()
    plt.subplot(313)

    plt.plot(frame_ids, yaws, linewidth=2,
             linestyle='-', color='darkred', label='yaw')
    plt.yticks(size=12)
    plt.ylabel('Yaw', size=14)
    plt.legend(loc='upper left', prop={'size': 10, 'weight': 'bold'})
    plt.xlabel('Frame Id', size=14)
    plt.xticks(size=12)

    plt.twinx()
    plt.plot(frame_ids, pitches, linewidth=2,
             linestyle='--', color='teal', label='pitch')

    plt.yticks(size=12)
    plt.ylabel('Pitch', size=14)
    plt.legend(loc='lower left', prop={'size': 10, 'weight': 'bold'})

    plt.savefig("QoE.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
