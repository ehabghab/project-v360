
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

    if len(sys.argv) < 2:
        print(
            "ERROR: python check_bw.py <recv_log>")
        sys.exit(1)

    bws = {}
    target = 1
    total_downtime = 0
    for line in open(sys.argv[1]).readlines():
        if "chunk" in line:
            continue
        data = line.split()
        recv_time = int(data[4])
        bw = float(data[5])
        if "inf" in data[5]:
            print("inf found")
            continue
        total_downtime += recv_time/1000.0
        if bws.get(target) is None:
            bws[target] = []
        bws[target].append(bw)
        if (total_downtime >= target):
            target += 1
            if (target == 10):
                break

    for sec in bws:
        bw = sum(bws[sec]) * 1.0 / len(bws[sec])
        print(str(sec)+":"+str(bw))


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
