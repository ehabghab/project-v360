import math
import matplotlib.pyplot as plt
import numpy as np
from os import system
import sys
import os

from numpy.core.fromnumeric import sort

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"]
})


def main():
    if len(sys.argv) < 2:
        print("Usage: python3.9 rebuffering_joinTime_CDF <play_log1> <play_log1_bw> <play_log1_delay> ... <play_logN> <play_logN_bw> <play_logN_delay>")
        sys.exit(1)

    files = []
    for i in range(1, len(sys.argv)):
        files.append(sys.argv[i])

    # key1: file, list of render_f(i) - render_f(i-1)
    file_rebuffer_time = {}
    for f in files:
        file_rebuffer_time[f] = []
        prev_render = -1
        for line in open(f, 'r').readlines():
            if "frame id" in line:
                continue
            data = line.split()
            render_time = int(data[2])
            if prev_render != -1:
                file_rebuffer_time[f].append((render_time-prev_render)-40)
            prev_render = render_time
    rebus = []
    c = 0
    for f in file_rebuffer_time:
        for x in file_rebuffer_time[f]:
            if x > 0:
                c += 1
                rebus.append(x)
    print(c)
    print(sum(rebus))

    bw = [3.1, 100, 100, 100]
    delay = [0, 20, 40, 100]
    colors = ['black', 'dodgerblue', 'seagreen', 'darkred']
    styles = ['-', '-.', '--', ':']
    plt.figure(figsize=(5, 3))
    plt.tight_layout()
    c = 0
    for f in sorted(file_rebuffer_time):
        print(f)
        #label = str(bw[c])+"mbps_"+str(delay[c])+"ms"
        sorted_data = np.sort(file_rebuffer_time[f])
        yvals = np.arange(len(sorted_data)) * 100. / \
            float(len(sorted_data) - 1)
        print(yvals)
        plt.plot(sorted_data, yvals, linewidth=2,
                 linestyle=styles[c], color=colors[c])
        c += 1

    plt.xticks(size=12)
    plt.yticks(size=12)

    #plt.legend(loc='best', prop={'size': 12, 'weight': 'bold'})
    plt.ylabel('\% of frames', size=12)
    plt.xlabel('Rebuffering (ms)', size=12)
    plt.ylim(85, 100.1)
    # plt.xlim(-1,10)
    # plt.show()
    plt.savefig("rebuffering.png", format="png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
