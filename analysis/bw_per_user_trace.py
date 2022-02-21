
import math
import matplotlib.pyplot as plt
import numpy as np
import sys
import ast
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times",
    "font.sans-serif": ["Times"]
})


def main():

    if len(sys.argv) < 3:
        print(
            "ERROR: python bw_per_user_trace.py <tile_per_frame_user> <quality_sizes>")
        sys.exit(1)

    # 1:[29, 30, 31, 32, 41, 42, 43, 44, 53, 54, 55, 56, 65, 66, 67, 68, 77, 78, 79, 80, 89, 90, 91, 92, 101, 102, 103, 104, 113, 114, 115, 116]
    chunk_tiles = {}
    for line in open(sys.argv[1], "r").readlines():
        frame = int(line.split(":")[0])
        chunk = (frame - 1) / 25
        if chunk_tiles.get(chunk) is None:
            chunk_tiles[chunk] = set()
        for tile in ast.literal_eval(line.split(":")[1]):
            chunk_tiles[chunk].add(tile)

    chunk_tile_quality_size = {}
    for line in open(sys.argv[2], "r"):
        quality_tile = line.split(":")[0]
        quality = int(quality_tile.split("_")[0])
        tile = int(quality_tile.split("_")[1])
        sizes = [float(size) for size in line.split(":")[1].split(",")]
        for chunk_id in range(0, len(sizes)):
            if chunk_tile_quality_size.get(chunk_id) is None:
                chunk_tile_quality_size[chunk_id] = {}
            if chunk_tile_quality_size[chunk_id].get(tile) is None:
                chunk_tile_quality_size[chunk_id][tile] = {}
            chunk_tile_quality_size[chunk_id][tile][quality] = sizes[chunk_id]

    second_size_per_quality = {}
    for chunk in chunk_tiles:
        second_size_per_quality[chunk] = {}
        for tile in chunk_tiles[chunk]:
            for quality in chunk_tile_quality_size[chunk_id][tile]:
                if second_size_per_quality[chunk].get(quality) is None:
                    second_size_per_quality[chunk][quality] = 0.0
                second_size_per_quality[chunk][quality] += chunk_tile_quality_size[chunk_id][tile][quality]

    x_axis = []
    bw_per_quality = {}
    for chunk in second_size_per_quality:
        x_axis.append(chunk)
        for quality in second_size_per_quality[chunk]:
            if bw_per_quality.get(quality) is None:
                bw_per_quality[quality] = []
            bw_per_quality[quality].append(
                second_size_per_quality[chunk][quality] * 8.0 / 1e6)

    plt.figure(figsize=(4, 2))
    plt.tight_layout()
    plt.subplot(111)

    colors = ["dodgerblue", "seagreen", "darkred"]
    styles = ["-", "-", "--"]
    c = 0
    for quality in bw_per_quality:
        plt.plot(
            x_axis, bw_per_quality[quality], linestyle=styles[c], linewidth=1.5, color=colors[c], label="quality = "+str(quality))
        c += 1
        print(sum(bw_per_quality[quality])/len(bw_per_quality[quality]))
    plt.grid(True)
    plt.legend(loc='best', prop={'size': 10,
               'weight': 'bold'}, edgecolor="black")
    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.ylim(0)
    plt.xlim(-1, 61)
    plt.ylabel('Bandwidth(mbps)', size=12)
    plt.xlabel('Time (second)', size=12)
    plt.savefig("bw_per_user_trace.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
