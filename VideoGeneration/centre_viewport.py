import numpy as np
import cv2
import os
import sys

input_dir = sys.argv[1]
output_yuv_dir = sys.argv[2]
output_png_dir = sys.argv[3]

if len(sys.argv) < 4:
    print('python3 ffmpeg_system.py yuv_viewport_dir yuv_output_dir png_output_dir')

if os.path.isdir(input_dir):
    print('Correct Input')
else:
    print('Give correct input directory')
    exit(0)

if os.path.isdir(output_yuv_dir):
    print('Output yuv directory exists.')
else:
    os.mkdir(output_yuv_dir)

if os.path.isdir(output_png_dir):
    print('Output png directory exists.')
else:
    os.mkdir(output_png_dir)

final_w = 3840
final_h = 1920

for name in os.listdir(input_dir):
    file = input_dir + name
    # file = 'TestYUV/1_1280X1280.yuv'

    id = file.split('/')[1].split('_')[0]
    w = int(file.split('_')[1].split('X')[0])
    h = int(file.split('_')[1].split('X')[1].split('.')[0])

    #ffmpeg -video_size 1280x1280 -i 1_1280X1280.yuv -vf "pad=3840:1920:(3840-1280)/2:(1920-1280)/2:black" padded-black.png
    corner_w = int((final_w - w)/2)
    corner_h = int((final_h - h)/2)

    output_yuv = output_yuv_dir + str(id) + '.yuv'
    output_png = output_png_dir + str(id) + '.png'

    cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + file + ' -vf "pad=' + str(final_w) + ':' + str(final_h) + ':' + str(corner_w) + ':' + str(corner_h) + ':black"' + ' ' + output_yuv

    print(cmd)

    os.system(cmd)

    #Uncomment the next lines if we want to see the png images for the generated yuv.
    # f = open(output_yuv, 'rb')
    #
    # l = f.read(int(3840 * 1920 * 3 / 2))
    #
    # yuv = np.frombuffer(l, dtype=np.uint8)
    # yuv1 = yuv.reshape(int(1920 * 1.5), 3840)
    #
    # bgr = cv2.cvtColor(yuv1, cv2.COLOR_YUV2BGR_I420)
    # cv2.imwrite(output_png, bgr)
