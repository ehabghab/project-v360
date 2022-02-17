

import matplotlib.pyplot as plt
import numpy as np
import sys


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times",
    "font.sans-serif": ["Times"]})


def main():

    if len(sys.argv) < 3:
        print("Usage error: python3 viewport_quality tile_per_frame_userN recv_log1 recv_log2 ... recv_logN ")
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

    recv_logs = []
    for i in range(2, len(sys.argv)):
        recv_logs.append(sys.argv[i])
    recv_chunk_quality = {}
    for recv_log in recv_logs:
        recv_chunk_quality[recv_log] = {}
        for line in open(recv_log).readlines():
            if "chunk" in line:
                continue
            data = line.split()
            chunk_id = int(data[0])
            tile_id = int(data[1])
            quality = int(data[2])
            recv_chunk_quality[recv_log][str(
                chunk_id)+"_"+str(tile_id)] = quality

    skipped_tiles = {}
    for line in open("results_Feb_16th[utility_flare_new_video]/result_5.5_flare_usr13/play_log_2022-02-17_08_16_36.txt").readlines():
        if "frame" in line:
            continue
        data = line.split()
        if len(data) == 4:
            frame = int(data[0])
            skipped_tiles[frame] = []
            for tile in data[3].split(","):
                skipped_tiles[frame].append(int(tile))

    vp_quality_avg = {}
    for recv_log in recv_chunk_quality:
        vp_quality_avg[recv_log] = []
        for frame in sorted(ground_truth):
            if frame > 1475:
                continue
            chunk_id = int(((frame-1) / 25)) + 1
            quality_sum = 0.
            total_tiles = 0.
            for tile in ground_truth[frame]:
                key = str(chunk_id)+"_"+str(tile)
                if recv_chunk_quality[recv_log].get(key) is None:
                    if "utility_skip_usr13" in recv_log:
                        quality_sum += 1
                    else:
                        quality_sum += 0
                else:
                    if "flare_skip" in recv_log:
                        if skipped_tiles.get(frame) is not None:
                            if tile not in skipped_tiles[frame]:
                                quality_sum += recv_chunk_quality[recv_log][key]
                        else:
                            quality_sum += recv_chunk_quality[recv_log][key]
                    else:
                        quality_sum += recv_chunk_quality[recv_log][key]
                total_tiles += 1.
            if total_tiles != 0:
                vp_quality_avg[recv_log].append(quality_sum/total_tiles)

    bw = [100, 100, 100, 100]
    delay = [0, 20, 40, 100]
    colors = ['dodgerblue', 'seagreen', 'darkred']
    styles = ['-', ':', '--']
    labels = ["utility", "flare-skip", "flare-buff"]

    plt.figure(figsize=(4, 2))
    plt.tight_layout()
    c = 0
    for f in recv_logs:
        label = str(bw[c])+"mbps_"+str(delay[c])+"ms"
        sorted_data = np.sort(vp_quality_avg[f])
        yvals = np.arange(len(sorted_data)) * 100.0 / \
            float(len(sorted_data) - 1)
        print(np.percentile(vp_quality_avg[f], 50))
        plt.plot(sorted_data, yvals, linewidth=2,
                 linestyle=styles[c], color=colors[c], label=labels[c])
        c += 1

    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.legend(loc='upper left', ncol=1, prop={'size': 10,
               'weight': 'bold'}, edgecolor="black")
    plt.ylabel('\% of frames', size=12)
    plt.xlabel('Avg. quality', size=12)
    # plt.ylim(.93,1.01)
    plt.xlim(0)
    # plt.show()
    plt.savefig("viewport_quality.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
