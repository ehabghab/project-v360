
import math
import matplotlib.pyplot as plt
import numpy as np
import sys

plt.rcParams.update({
    "text.usetex": True})


def main():

    if len(sys.argv) < 3:
        print(
            "ERROR: python switches_ts.py <user_tiles_per_frame> <tile_sizes>")
        sys.exit(1)
    tiles_per_frame = {}
    for line in open(sys.argv[1]).readlines():
        data = line.split(":")
        frame = int(data[0])
        tiles = data[1].replace("[", "").replace("]\n", "").split(",")
        tiles_list = []
        for tile in tiles:
            tiles_list.append(int(tile))
        tiles_per_frame[frame] = tiles_list

    cumlative_tiles_per_frame = {}
    current_chunk_tiles = set()
    for frame in tiles_per_frame:
        for tile in tiles_per_frame[frame]:
            if (frame - 1) % 25 == 0:
                if cumlative_tiles_per_frame.get(frame) is None:  # init
                    cumlative_tiles_per_frame[frame] = set()
                    current_chunk_tiles = set()
                cumlative_tiles_per_frame[frame].add(tile)
                current_chunk_tiles.add(tile)
            else:
                if tile not in current_chunk_tiles:
                    if cumlative_tiles_per_frame.get(frame) is None:
                        cumlative_tiles_per_frame[frame] = set()
                    cumlative_tiles_per_frame[frame].add(tile)
                    current_chunk_tiles.add(tile)

    tile_sizes = {}
    for line in open(sys.argv[2]).readlines():
        data = line.split(":")
        quality_id = int(data[0].split("_")[0])
        if quality_id == 2:
            break
        tile_id = int(data[0].split("_")[1])
        tile_chunks_sizes = data[1].replace(
            "[", "").replace("]\n", "").split(",")
        tile_sizes[tile_id] = []
        for sizes in tile_chunks_sizes:
            tile_sizes[tile_id].append(int(sizes))

    chunk_size = {}
    chunk_id = -1
    for frame in cumlative_tiles_per_frame:
        if (frame - 1) % 25 == 0:
            chunk_id += 1
            if chunk_id == 59:
                break
            chunk_size[chunk_id] = 0

        for tile in cumlative_tiles_per_frame[frame]:
            chunk_size[chunk_id] += tile_sizes[tile][chunk_id]

    x_chunk_size = []
    y_chunk_size = []
    for chunk_id in chunk_size:
        x_chunk_size.append(chunk_id * 25)
        y_chunk_size.append(float(
            "%.2f" % (chunk_size[chunk_id] * 8.0 / 1e6)))

    x_num_sw = []
    y_num_sw = []
    for frame in cumlative_tiles_per_frame:
        if (frame - 1) % 25 == 0:
            continue
        x_num_sw.append(frame)
        y_num_sw.append(len(cumlative_tiles_per_frame[frame]))

    count_chunk = {}
    for frame in x_num_sw:
        chunk_id = int((frame - 1) / 25)
        if count_chunk.get(chunk_id) is None:
            count_chunk[chunk_id] = 0
        count_chunk[chunk_id] += 1

    x_t = []
    for chunk_id in range(0, 60):
        if count_chunk.get(chunk_id) is None:
            x_t.append(0)
        else:
            x_t.append(count_chunk[chunk_id])

    print(sum(x_t)/len(x_t))

    plt.figure(figsize=(8, 4))
    plt.tight_layout()
    plt.subplot(111)
    plt.scatter(x_num_sw, y_num_sw, s=10,
                marker='x', color='dodgerblue')
    plt.xticks(size=12)
    plt.yticks(size=12)

    xposition = [i for i in range(1, 1500, 25)]
    for xc in xposition:
        plt.axvline(x=xc, color='lightgray', linewidth=.5, linestyle='--')
    plt.ylim(0)
    plt.xlim(-5, 1476)
    plt.ylabel('\# of tiles', size=12)
    plt.xlabel('Frame Id', size=14)
    plt.savefig("switches_ts.png", bbox_inches='tight', dpi=300)
    #####################################################################

    plt.figure(figsize=(8, 4))
    plt.tight_layout()
    plt.subplot(111)
    plt.scatter(x_chunk_size, y_chunk_size, s=10,
                marker='x', color='dodgerblue', zorder=3)
    plt.axhline(y=3.1, color='lightgray',
                linewidth=1.5, linestyle='--', zorder=2)

    plt.xticks(size=12)
    plt.yticks(size=12)
    plt.ylim(0)
    plt.xlim(-5, 1476)
    # plt.legend(loc='best', prop={'size': 10, 'weight': 'bold'})
    plt.ylabel('Bandwidth (mbps)', size=12)
    plt.xlabel('Frame Id', size=14)
    plt.savefig("switches_bw_ts.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
