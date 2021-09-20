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


def plot_no_opt():
    res1 = open("YUV_decoding.txt")
    sws = []
    decd_lat = []
    decd_lat_wo_sws = []
    for line in res1.readlines():
        if "Sws" in line:
            sws_t = int(line.split(":")[1])
            sws.append(sws_t)
        elif "Total Decoding" in line:
            t = int(line.split(":")[1])
            decd_lat.append(t)
            decd_lat_wo_sws.append(t - sws_t)

    plt.figure(figsize=(5, 3))
    plt.tight_layout()

    sorted_data = np.sort(sws)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    plt.plot(sorted_data, yvals, linewidth=2, color='darkred', label='sws')

    sorted_data = np.sort(decd_lat_wo_sws)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    plt.plot(sorted_data,
             yvals,
             linewidth=2,
             color='seagreen',
             label='decode - sws')

    sorted_data = np.sort(decd_lat)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    plt.plot(sorted_data,
             yvals,
             linewidth=2,
             color='dodgerblue',
             label='decode')

    plt.xticks(size=12)
    plt.yticks(size=12)
    #plt.title("[1-thread, no opt]", size=16)
    plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    plt.ylabel('Frac. of tiles', size=14)
    plt.xlabel('latency (ms)', size=14)
    #plt.ylim(0, 1)
    plt.xlim(-1, 20)
    # plt.show()
    plt.savefig("latency_no_opt_XX.png", bbox_inches='tight', dpi=300)


def plot_no_opt_m():
    res1 = open("res_dec_1th.txt")
    decd_lat1 = []
    for line in res1.readlines():
        if "Total Decoding" in line:
            t = int(line.split(":")[1])
            decd_lat1.append(t)

    res3 = open("YUV_decoding.txt")
    decd_lat3 = []
    for line in res3.readlines():
        if "Total Decoding" in line:
            t = int(line.split(":")[1])
            decd_lat3.append(t)

    plt.figure(figsize=(5, 3))
    plt.tight_layout()
    print(np.percentile(decd_lat1, 50))
    print(np.percentile(decd_lat3, 50))
    sorted_data = np.sort(decd_lat1)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    plt.plot(sorted_data,
             yvals,
             linewidth=2,
             color='darkred',
             label='1-thread')

    sorted_data = np.sort(decd_lat3)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    plt.plot(sorted_data,
             yvals,
             linewidth=2,
             color='dodgerblue',
             label='8-threads')

    plt.xticks(size=12)
    plt.yticks(size=12)
    plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    plt.ylabel('Frac. of tiles', size=14)
    plt.xlabel('latency (ms)', size=14)
    #plt.ylim(0, 1)
    plt.xlim(-1, 20)
    # plt.show()
    plt.savefig("latency_no_opt_1th_8th.png", bbox_inches='tight', dpi=300)


def plot_opt():
    res1 = open("decoding/res1_op.txt")
    decd_lat = []
    for line in res1.readlines():
        if "Total Decoding" in line:
            t = int(line.split(":")[1])
            decd_lat.append(t)

    plt.figure(figsize=(5, 3))
    plt.tight_layout()

    sorted_data = np.sort(decd_lat)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    plt.plot(sorted_data,
             yvals,
             linewidth=2,
             color='dodgerblue',
             label='decode')

    plt.xticks(size=12)
    plt.yticks(size=12)
    plt.title("[1-thread, opt]", size=16)
    plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    plt.ylabel('Frac. of tiles', size=14)
    plt.xlabel('latency (ms)', size=14)
    #plt.ylim(0, 1)
    plt.xlim(-1, 20)
    # plt.show()
    plt.savefig("latency_opt.png", bbox_inches='tight', dpi=300)


def main():
    plot_no_opt()
    #plot_opt()


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
