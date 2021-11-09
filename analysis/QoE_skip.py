
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

    missed_tiles = {}
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

        missed_tiles_list = data[3] if len(data) == 4 else None
        if missed_tiles_list != None:
            missed_tiles[int(data[0])] = [int(x) for x in data[3].split(',')]

    yaw_pred_per_frame = {}  # key: frame, value: list of yaw predictions
    pitch_pred_per_frame = {}  # key: frame, value: list of pitch predictions
    for line in open(sys.argv[5]):
        if "frame" in line:
            continue
        frame = int(line.split()[0].split("(")[0])
        coordinates = line.split()[1].replace(")", "").replace(
            "(", "").split("--")[1:-1]
        yaw_pred_per_frame[frame] = []
        pitch_pred_per_frame[frame] = []
        for coor in coordinates:
            coor = coor.split(",")
            yaw = float(coor[0])
            pitch = float(coor[1])
            yaw_pred_per_frame[frame].append(yaw)
            pitch_pred_per_frame[frame].append(pitch)

    half_sec_yaw = []
    half_sec_pitch = []
    pred_x = []
    for frame in yaw_pred_per_frame:
        pred_x.append(frame + 13)
        yaw_pred = yaw_pred_per_frame[frame][12]
        pitch_pred = pitch_pred_per_frame[frame][12]
        """acc_yaw = 100 - \
            abs(((yaws[frame - 1] - yaw_pred) / yaws[frame - 1]) * 100)
        acc_pitch = 100 - \
            abs(((pitches[frame - 1] - pitch_pred) / pitches[frame - 1]) * 100)
        if (acc_yaw) < 0:
            print(yaw_pred)
            print(yaws[frame - 1])
            print(acc_yaw)
            print("----")
        """
        half_sec_yaw.append(yaw_pred)
        half_sec_pitch.append(pitch_pred)

    fraction_missed = []
    vp_quality_avg = []
    for frame in ground_truth:
        if frame > 1475:
            break
        chunk_id = int(((frame-1) / 25)) + 1
        quality_sum = 0.
        missed_tiles_sum = 0.
        total_tiles = 0.
        for tile in ground_truth[frame]:
            missed = False
            key = str(chunk_id)+"_"+str(tile)
            if missed_tiles.get(frame) is not None:
                if tile in missed_tiles[frame]:
                    missed_tiles_sum += 1
                    missed = True
            if recv_chunk_quality.get(key) is not None and not missed:
                quality_sum += recv_chunk_quality[key]

            total_tiles += 1.

        if total_tiles != 0:
            vp_quality_avg.append(quality_sum/total_tiles)
            fraction_missed.append(missed_tiles_sum/total_tiles)

    bw = [100, 100, 100, 100]
    delay = [0, 20, 40, 100]
    colors = ['black', 'dodgerblue', 'seagreen', 'darkred']
    styles = ['-', '-.', '--', ':']

    frame_ids = [i for i in range(1, 1476)]
    plt.figure(figsize=(16, 12))
    plt.tight_layout()
    plt.subplot(411)
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
    # plt.xlabel('Frame Id', size=14)

    plt.subplot(412)
    plt.plot(frame_ids, fraction_missed, linewidth=2,
             linestyle='-', color='seagreen')
    plt.xticks(size=12)
    plt.yticks([0, .2, .4, .6, .8, 1], [
               'full view', .2, .4, .6, .8, 'blank'], size=12)

    # plt.legend(loc='best', prop={'size': 10, 'weight': 'bold'})
    plt.ylabel('Fraction of skipped tiles', size=14)
    # plt.xlabel('Frame Id', size=14)

    # plt.ylim(.93,1.01)
    # plt.xlim(-1,10)
    # plt.show()

    plt.subplot(413)

    plt.plot(frame_ids, yaws, linewidth=2,
             linestyle='-', color='red', label='actual')

    plt.plot(pred_x, half_sec_yaw, linewidth=2,
             linestyle='-.', color='darkred', label='pred')

    plt.yticks(size=12)
    plt.ylabel('Yaw', size=14)
    plt.legend(loc='upper left', prop={'size': 10, 'weight': 'bold'})
    # plt.xlabel('Frame Id', size=14)
    plt.xticks(size=12)

    plt.subplot(414)

    plt.plot(frame_ids, pitches, linewidth=2,
             linestyle='-', color='red', label='actual')

    plt.plot(pred_x, half_sec_pitch, linewidth=2,
             linestyle='-.', color='darkred', label='pred')

    plt.yticks(size=12)
    plt.ylabel('Pitch', size=14)
    plt.legend(loc='upper left', prop={'size': 10, 'weight': 'bold'})
    plt.xlabel('Frame Id', size=14)
    plt.xticks(size=12)

    # plt.twinx()
    # plt.plot(frame_ids, pitches, linewidth=2,
    #         linestyle='--', color='teal', label='pitch')

    # plt.yticks(size=12)
    # plt.ylabel('Pitch', size=14)
    # plt.legend(loc='lower left', prop={'size': 10, 'weight': 'bold'})

    plt.savefig("QoE.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
