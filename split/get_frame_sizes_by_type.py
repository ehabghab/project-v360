import numpy as np
import os
import sys
import subprocess
import matplotlib.pyplot as plt


def main():
    if len(sys.argv) < 2:
        print(
            "Error: python get_frame_sizes_by_type.py <quality_dir_1> ... <quality_dir_n>")
        sys.exit(1)

    iframe_size_to_chunk = {}
    command = "ffprobe -show_frames %s | grep \"pkt_size\""
    for pathIdx in range(1, len(sys.argv)):
        path = sys.argv[pathIdx]
        tiles_dirs = os.listdir(path)
        qualityIdx = int(path.split("/")[1])
        iframe_size_to_chunk[qualityIdx] = []
        for tile_dir in sorted(tiles_dirs):
            if "DS_Store" in tile_dir:
                continue
            tile_dir_path = path+"/"+tile_dir
            chunks = os.listdir(tile_dir_path)
            print(tile_dir_path)
            print("=============")

            for chunk in chunks:
                if "DS_Store" in chunk:
                    continue
                frame_path = tile_dir_path + "/"+chunk
                process = subprocess.Popen(
                    command % (frame_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                stdout, stderr = process.communicate()
                frame_sizes = [int(i) for i in stdout.replace(
                    "pkt_size=", "").split("\n")[:-1]]
                chunk_size = sum(frame_sizes) * 1.0
                frac = frame_sizes[0] / chunk_size
                iframe_size_to_chunk[qualityIdx].append(frac * 100)

    plt.figure(figsize=(8, 6))
    plt.subplot(111)
    colors = ["dodgerblue", "seagreen", "darkred"]
    styles = ["-", "-.", "--"]
    for quality in iframe_size_to_chunk:
        sorted_data = np.sort(iframe_size_to_chunk[quality])
        yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
        plt.plot(sorted_data, yvals, linewidth=3,
                 linestyle=styles[quality - 1], color=colors[quality - 1], label="Q"+str(quality))
    plt.xticks(fontweight="bold", size=14)
    plt.yticks([0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1],
               fontweight="bold", size=14)
    plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    plt.xlabel('% of Iframe Size to Chunk', fontweight="bold", size=14)
    plt.ylabel('Fraction of chunks', fontweight="bold", size=14)
    plt.grid()
    # plt.xlim(1000)
    # plt.ylim(.96, 1.001)  # ,1)
    # plt.show()
    plt.savefig("iframe_size_to_chunk.png", dpi=300)


if __name__ == "__main__":
    main()
