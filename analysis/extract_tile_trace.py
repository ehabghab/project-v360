
from pyquaternion import Quaternion
import math
import matplotlib.pyplot as plt
import numpy as np
from os import walk
import os
import matplotlib.patches as mpatches

# plt.rcParams.update({
#    "text.usetex": True,
#    "font.family": "sans-serif",
#    "font.sans-serif": ["Helvetica"]})

videos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
          14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
FOV = 100


def plotMap(tileMap, cx, cy, tileWidth, tileHeight):
    f = plt.figure(figsize=(12, 6))
    ax = f.add_subplot(111)

    for y in range(180, 0, -tileHeight):
        for x in range(0, 360, tileWidth):
            xaxis = x+(tileWidth / 2)

            yaxis = y-(tileHeight/2)
            plt.text(xaxis, yaxis, str(
                tileMap[x][y]), horizontalalignment='center', verticalalignment='center', fontsize=10)

    minor_ticks = np.arange(0, 361, tileWidth)
    plt.xticks(minor_ticks)

    ax.set_xticks(minor_ticks, minor=True)
    minor_ticks = np.arange(0, 181, tileHeight)
    plt.yticks(minor_ticks)

    ax.set_yticks(minor_ticks, minor=True)
    ax.set_xlabel('Yaw')
    ax.set_ylabel('Pitch')

    # And a corresponding grid
    ax.grid(which='both')
    plt.grid()
    plt.xlim(0, 360, tileWidth)
    plt.ylim(0, 180)
    plt.scatter(cx, cy, linewidth='8', marker='x', color='r')
    offset = FOV/2.0

    x1 = cx - offset
    if (x1 < 0):
        x1 = 360 + x1

    x2 = cx + offset
    if (x2 > 360):
        x2 = x2 - 360

    x3 = x1
    x4 = x2
    y1 = cy - offset
    if (y1 < 0):
        y1 = (180 + y1)

    y2 = cy + offset
    x5 = x1
    x6 = x2
    if (y2 > 180):
        y2 = (y2 - 180)

    plt.scatter(x3, y1, color='g', linewidth='3',
                marker='^' if x3 == x1 else "v")
    plt.scatter(x5, y2, color='r', linewidth='3',
                marker='v' if x5 == x1 else "^")
    plt.scatter(x4, y1, color='g', linewidth='3',
                marker='^' if x4 == x2 else "v")
    plt.scatter(x6, y2, color='r', linewidth='3',
                marker='v' if x6 == x2 else "^")

    plt.show()


def getTiles(map, cx, cy, tileWidth, tileHeight):
    offset = FOV/2.0
    h = False
    v = False

    x1 = cx - offset
    if (x1 < 0):
        x1 = 360 + x1
        h = True

    x2 = cx + offset
    if (x2 > 360):
        x2 = x2 - 360
        h = True

    x3 = x1
    x4 = x2
    y1 = cy - offset
    if (y1 < 0):
        y1 = (180 + y1)
        v = True

    y2 = cy + offset
    x5 = x1
    x6 = x2
    if (y2 > 180):
        y2 = (y2 - 180)
        v = True

    # up left x5,y2
    # up right x6,y2
    # down left x3,y1
    # down right x4,y1

    # flipped or not
    # xaxis are wrapped or not!
    tiles = set()

    x3 = int(x3 / tileWidth) * tileWidth
    x5 = int(x5 / tileWidth) * tileWidth
    x4 = (int(x4 / tileWidth) * tileWidth +
          1) if x4 % 30 != 0 else (int(x4 / tileWidth) * tileWidth)
    x6 = (int(x6 / tileWidth) * tileWidth +
          1) if x6 % 30 != 0 else (int(x6 / tileWidth) * tileWidth)

    y1 = ((math.ceil(y1 / tileHeight) * tileHeight) -
          1) if y1 % 15 != 0 else (math.ceil(y1 / tileHeight) * tileHeight)
    y2 = math.ceil(y2 / tileHeight) * tileHeight
    #print("("+str(x5)+","+str(y2)+")  --->   "+"("+str(x6)+","+str(y2)+")")
    #print("("+str(x3)+","+str(y1)+")  --->   "+"("+str(x4)+","+str(y1)+")")
    if not h and not v:
        for j in range(int(y2), int(y1), -tileHeight):
            for i in range(int(x5), int(x6), tileWidth):
                tiles.add(map[i][j])

    elif not h and v:
        for j in range(int(y2), int(0), -tileHeight):
            for i in range(int(x5), int(x6), tileWidth):
                tiles.add(map[i][j])

        for j in range(int(180), int(y1), -tileHeight):
            for i in range(int(x3), int(x4), tileWidth):
                tiles.add(map[i][j])

    elif h and not v:
        for j in range(int(y2), int(y1), -tileHeight):
            for i in range(int(0), int(x4), tileWidth):
                tiles.add(map[i][j])

        for j in range(int(y2), int(y1), -tileHeight):
            for i in range(int(x5), int(360), tileWidth):
                tiles.add(map[i][j])

    else:

        for j in range(int(180), int(y1), -tileHeight):
            for i in range(int(0), int(x4), tileWidth):
                tiles.add(map[i][j])

        for j in range(int(180), int(y1), -tileHeight):
            for i in range(int(x3), int(360), tileWidth):
                tiles.add(map[i][j])

        for j in range(int(y2), int(0), -tileHeight):
            for i in range(int(0), int(x6), tileWidth):
                tiles.add(map[i][j])

        for j in range(int(y2), int(0), -tileHeight):
            for i in range(int(x5), int(360), tileWidth):
                tiles.add(map[i][j])

    return tiles


def generateMAP(tileWidth, tileHeight):
    map = {}
    blockNum = 1
    for y in range(180, 0, -tileHeight):
        for x in range(0, 360, tileWidth):
            if map.get(x, None) == None:
                map[x] = {}
            map[x][y] = blockNum
            blockNum += 1
    return map


def getData(data, video, chunkLength, tileWidth, tileHeight, tileMap):
    # frames watched within tile. key is (user id --> sec -->tile), value number of frames.
    watched_frames_in_tiles = {}
    # index of watched frames in chunk, key is (user id --> chunkNum), value list of frames number within tile.
    num_frames_in_tile = {}
    num_tiles_in_FOV = {}  # number of tiles in a single FOV
    wasted_area_in_watched_frame = {}
    yaws = {}
    pitches = {}
    for vID in data:
        if vID != video:
            continue
        for uID in data[vID]:
            yaws[uID] = []
            pitches[uID] = []
            FOVNum = 1  # number of frames in second (frame counter)
            startTime = -1
            prevFrameTime = 0
            chunkID = -1
            watched_frames_in_tiles[uID] = {}
            num_frames_in_tile[uID] = {}
            num_tiles_in_FOV[uID] = {}
            wasted_area_in_watched_frame[uID] = {}
            for row in data[vID][uID]:
                timestamp = row[0]  # sec.msec
                yaw = math.degrees(row[1]) + 180
                pitch = math.degrees(row[2]) + 90
                roll = math.degrees(row[3])
                if startTime == -1:  # first frame in first chunk of the video.
                    startTime = timestamp * 1000
                    chunkID = 0
                    FOVNum = 1

                # calibrate the time to start from zero.
                timestampCal = timestamp*1000 - startTime

                # if we moved to next chunk in video
                if timestampCal >= chunkID*chunkLength + chunkLength:
                    chunkID += 1
                    FOVNum = 1

                # frames are 40msec apart (25FPS).
                if (timestampCal - prevFrameTime) >= 40 or prevFrameTime == 0:
                    yaws[uID].append(yaw)
                    pitches[uID].append(pitch)
                    prevFrameTime += 40
                    tiles = getTiles(
                        tileMap, yaw, pitch, tileWidth, tileHeight)
                    if watched_frames_in_tiles[uID].get(chunkID, None) == None:
                        watched_frames_in_tiles[uID][chunkID] = {}
                        wasted_area_in_watched_frame[uID][chunkID] = {}
                    num_tiles_in_FOV[uID][chunkID] = {}

                    # to calcuate the total area requested (GRAY AREA)
                    num_tiles_in_FOV[uID][chunkID][FOVNum] = len(tiles)
                    # track frames in tile which have been watched by user.
                    for tile in tiles:
                        if watched_frames_in_tiles[uID][chunkID].get(tile, None) == None:
                            watched_frames_in_tiles[uID][chunkID][tile] = list(
                            )
                        watched_frames_in_tiles[uID][chunkID][tile].append(
                            FOVNum)

                    # for each frame watched in a tile what was the area used.

                    # the FPS for that second.
                    num_frames_in_tile[uID][chunkID] = FOVNum
                    FOVNum += 1

    return watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV, yaws, pitches


def main():
    # get filenames of all traces.
    files = list()
    for (dirpath, dirnames, filenames) in walk("./traces"):
        for fname in filenames:
            if ".csv" in fname:
                files.append(dirpath+"/"+fname)

    for i in range(1, 2):
        print("Video:"+str(i))
        video = i
        if video == 15 or video == 16:
            continue

        # retrieve traces of interest.
        data = {}
        for fname in files:
            vID = int(fname.split("vID_")[1].split("_")[0])
            uID = int(fname.split("uID_")[1].split("_")[0])
            if vID != video:
                continue
            if data.get(vID, None) == None:
                data[vID] = {}
            data[vID][uID] = list()
            f = open(fname, 'r')
            for line in f.readlines():
                if "yaw" in line:
                    continue
                temp = line.split(',')
                playbackTime = float(temp[0])
                x = float(temp[1])
                y = float(temp[2])
                z = float(temp[3])
                data[vID][uID].append([playbackTime, x, y, z])

        chunkLength = 1000  # chunk length in millisecond
        widths = [30]
        heights = [15]
        for tileWidth, tileHeight in zip((widths), (heights)):
            tileMap = generateMAP(tileWidth, tileHeight)
            watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV,\
                yaws, pitches = getData(data, video, chunkLength,
                                        tileWidth, tileHeight, tileMap)

        for uID in yaws:
            fi = open("traces_system/vp_corr_per_frame_user_" +
                      str(uID)+".txt", 'w')
            for x, y in zip(yaws[uID], pitches[uID]):
                fi.write(str(x)+","+str(y)+"\n")
            fi.close()

        for user_id in watched_frames_in_tiles:
            tiles_per_frame = {}
            frames_count = 0
            for chunk_id in sorted(watched_frames_in_tiles[user_id]):
                for tile in watched_frames_in_tiles[user_id][chunk_id]:
                    for frame_id in watched_frames_in_tiles[user_id][chunk_id][tile]:
                        if tiles_per_frame.get(frame_id + frames_count) is None:
                            tiles_per_frame[frame_id+frames_count] = []
                        tiles_per_frame[frame_id+frames_count].append(tile)
                frames_count += num_frames_in_tile[user_id][chunk_id]

            chunk_in_sec = {}
            fi = open("traces_system/tiles_per_frame_user_" +
                      str(user_id)+".txt", 'w')
            frame_id = 1
            FPS = 25
            for frame in sorted(tiles_per_frame):
                fi.write(str(frame_id)+":"+str(tiles_per_frame[frame_id])+"\n")
                chunk_id = (frame_id - 1) / 25
                if chunk_in_sec.get(chunk_id+1) is None:
                    chunk_in_sec[chunk_id+1] = set()

                for tile in tiles_per_frame[frame_id]:
                    chunk_in_sec[chunk_id+1].add(tile)
                frame_id += 1

            fi.close()


if __name__ == "__main__":
    main()
