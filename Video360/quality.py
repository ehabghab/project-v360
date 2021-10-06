
import math
import matplotlib.pyplot as plt
import numpy as np
from os import system as sys
import os

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"]})


def main():
    c_file = open("res.txt")
    chunk_tile_quality = {}
    for line in c_file.readlines():
        data = line.split("/")
        quality = int(data[8])
        tile = int(data[9])
        chunk = int(data[10].split(".")[0])
        if chunk_tile_quality.get(chunk) is None:
            chunk_tile_quality[chunk] = {}
        chunk_tile_quality[chunk][tile] = quality

    ground_truth = {}
    for line in open("tiles_per_frame_user_3.txt").readlines():
        data = line.split(":")
        frame = int(data[0])
        tiles = data[1].replace("[", "").replace("]\n", "").split(",")
        ground_truth[frame] = tiles

    frame_quality = {}
    for frame in ground_truth:
        chunk = int(((frame - 1) / 25) + 1)
        if chunk > 59:
            break
        frame_quality[frame] = []
        for tile in ground_truth[frame]:
            frame_quality[frame].append(chunk_tile_quality[chunk][int(tile)])

    low = []
    high = []
    frame_id = []
    for frame in frame_quality:
        low_q = frame_quality[frame].count(1)
        high_q = frame_quality[frame].count(2)

        per_low = (low_q * 1. / len(frame_quality[frame])) * 100
        per_high = (high_q * 1. / len(frame_quality[frame])) * 100

        low.append(per_low)
        high.append(per_high)
        frame_id.append(frame)

    rebuffering_frames = [165, 188, 192, 201, 431, 566, 730,
                          735, 890, 1103, 1181, 1188, 1334, 1341, 1376, 1382]
    plt.figure(figsize=(16, 5))
    plt.subplot(111)
    plt.grid(axis='y', linestyle='--', zorder=1)
    plt.bar(frame_id, low, align='edge', color='r',
            label='low quality', width=1, zorder=2)
    plt.bar(frame_id, high, align='edge', color='dodgerblue',
            label='high quality', width=1, zorder=2, bottom=low)

    first = True
    for xc in rebuffering_frames:
        if first:
            plt.axvline(x=xc, ymax=.833, color='k',
                        linestyle='--', label="rebuffering")
            first = False
        else:
            plt.axvline(x=xc, ymax=.833, color='k',
                        linestyle='--')
    chunks = [x for x in range(0, 1476, 75)]
    chunks_labels = [int((x/25)) for x in range(0, 1476, 75)]

    plt.legend(loc='upper left', ncol=3, prop={'size': 12})
    plt.xlabel('Video id', size=14)
    plt.ylabel('Average switch latency (KB)', size=14)
    plt.xticks(chunks, chunks_labels, size=12)
    plt.yticks(size=12)
    plt.xlim(-10, 1485)
    plt.ylim(0, 120)
    # plt.grid(True)
    plt.savefig("switch_latency_bar.png", dpi=300,
                bbox_inches='tight', pad_inches=0.04)
    plt.close()


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
