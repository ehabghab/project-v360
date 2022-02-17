import numpy as np
import os
import math
import threading


def split_thread(idx, dir, st_frame, en_frame):
    video = open("video_original.yuv", 'rb')
    print("Thread#"+str(idx)+" "+str(st_frame)+":"+str(en_frame))
    frameWidth = 3840
    frameHeight = 1920

    widthTiles = 12
    heightTiles = 12
    heightRange = frameHeight/heightTiles
    widthRange = frameWidth/widthTiles

    files = {}
    for i in range(0, heightTiles):
        files[i] = {}
        for j in range(0, widthTiles):
            files[i][j] = open(dir+"/r_" +
                               str(i+1)+"_c_"+str(j+1)+"th"+str(idx)+".yuv", "w")

    video.seek(frameWidth * frameHeight * 1.5 * st_frame, 0)
    for frame in range(st_frame, en_frame+1):
        print("Thread#"+str(idx)+" --> splitting frame #"+str(frame))
        yVal = {}
        # Y values
        if idx == 0:
            print("r-31")
        for r in range(0, frameHeight):
            if idx == 0:
                print("r-34")
            yVal[r] = list()
            for c in range(0, frameWidth):
                if idx == 0:
                    print("r-38-1")
                byte = video.read(1)
                yVal[r].append(byte)
        if idx == 0:
            print("r-38")

        uVal = {}
        for r in range(0, frameHeight/4):
            uVal[r] = list()
            for c in range(0, frameWidth):
                byte = video.read(1)
                uVal[r].append(byte)
        if idx == 0:
            print("r-47")

        vVal = {}
        for r in range(0, frameHeight/4):
            vVal[r] = list()
            for c in range(0, frameWidth):
                byte = video.read(1)
                vVal[r].append(byte)
        if idx == 0:
            print("r-56")

        #frameHeight = 1080
        #frameWidth = 1920
        yValues = {}
        uValues = {}
        vValues = {}
        for i in range(0, heightTiles):  # row
            yValues[i] = {}
            uValues[i] = {}
            vValues[i] = {}

            for j in range(0, widthTiles):  # cols
                yValues[i][j] = list()
                uValues[i][j] = list()
                vValues[i][j] = list()

                stHeightRange = heightRange*i
                enHeightRange = heightRange*(i+1)
                stWidthRange = widthRange*j
                enWidthRange = widthRange*(j+1)

                if i == heightTiles - 1:
                    enHeightRange = frameHeight
                if j == widthTiles - 1:
                    enWidthRange = frameWidth

                # subblock y values
                for ii in range(stHeightRange, enHeightRange):
                    for jj in range(stWidthRange, enWidthRange):
                        # print str(stHeightRange)+"-->"+str(enHeightRange)+", "+str(stWidthRange)+"-->"+str(enWidthRange)
                        yValues[i][j].append(yVal[ii][jj])
                # subblock u/v values.
                prev = -1
                for ii in range(stHeightRange, enHeightRange, 2):
                    row = ii/4
                    for jj in range(stWidthRange, enWidthRange, 2):
                        if prev == row:
                            col = (frameWidth/2) + (jj/2)
                        else:
                            col = jj/2
                        uValues[i][j].append(uVal[row][col])
                        vValues[i][j].append(vVal[row][col])

                    prev = row
        if idx == 0:
            print("r-102")

        for i in yValues:
            for j in yValues[i]:
                for x in yValues[i][j]:
                    files[i][j].write(x)
                for x in uValues[i][j]:
                    files[i][j].write(x)
                for x in vValues[i][j]:
                    files[i][j].write(x)
        if idx == 0:
            print("r-113")


def main():
    # 1920x960
    frameWidth = 3840
    frameHeight = 1920

    widthTiles = 12
    heightTiles = 12

    dir = "YuvW"+str(widthTiles)+"H"+str(heightTiles)+"_newt"
    try:
        os.mkdir(dir)
    except OSError as error:
        True

    start_frame = 0.0
    end_frame = 1500.0
    num_threads = 8.0
    frames_per_tile = math.ceil((end_frame - start_frame) / num_threads)

    st = 0
    threads = []
    for i in range(0, int(num_threads)):
        en = st + frames_per_tile
        en = min(end_frame, en)
        t1 = threading.Thread(target=split_thread,
                              args=(i, dir, int(st), int(en-1)))
        t1.start()
        threads.append(t1)
        st = en
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
