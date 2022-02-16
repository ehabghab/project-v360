import numpy as np
import os


def main():
    video = open("video_original.yuv", 'rb')
    # 1920x960
    frameWidth = 3840
    frameHeight = 1920

    widthTiles = 12
    heightTiles = 12

    tile_width = frameWidth / widthTiles
    tile_height = frameHeight / heightTiles

    dir = "YuvW"+str(widthTiles)+"H"+str(heightTiles)+"_test"
    try:
        os.mkdir(dir)
    except OSError as error:
        True

    for w in range(0, widthTiles):
        for h in range(0, heightTiles):
            crop_w = w * tile_width
            crop_h = h * tile_height

            output_name = dir + "/r_"+str(h+1)+"_c_"+str(w+1)+".yuv"
            cmd = 'ffmpeg -video_size ' + str(frameWidth) + 'x' + str(frameHeight) + ' -i video_original.yuv -filter:v "crop=' + \
                str(tile_width)+':'+str(tile_height) + ':' + \
                str(crop_w) + ':' + str(crop_h) + '" ' + output_name

            os.system(cmd)


if __name__ == "__main__":
    main()
