import os
import sys

if len(sys.argv) < 5:
    print('python3 crop.py yuv_viewport_dir viewport_centre_coordinate yuv_output_dir png_output_dir')
    exit(1)

input_dir = sys.argv[1]

# Currently we are not using the viewport centre coordinate,
# assuming the centre of the viewport frame is same as center of user.
# But we need to use it at some point.
input_vp_corr = sys.argv[2]

output_yuv_dir = sys.argv[3]
output_png_dir = sys.argv[4]

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


#Assuming the viewport is 100x100, for a 3840x1920 frame, the viewport comes to 1066x1066.
vp_h = 1066
vp_w = 1066

filenames = os.listdir(input_dir)

"""
file = input_vp_corr
data = open(file, 'r')
info = data.readlines()

i = 1
centre = {}
for l in range(0, 1475):
    centre[i] = {}
    line = info[l]
    yaw = float(line.split(',')[0])
    pitch = float(line.split(',')[1].replace('\n', ''))
    centre[i]['yaw'] = yaw*32/3
    centre[i]['pitch'] = pitch*32/3
    i += 1
"""

for name in filenames:

    f = int(name.split('_')[0])
    w = int(name.split('_')[1].split('X')[0])
    h = int(name.split('_')[1].split('X')[1].split('.')[0])

    output_yuv = ' ' + output_yuv_dir + str(f) + '.yuv'
    output_png = ' ' + output_png_dir + str(f) + '.png'

    # We want to cut from left (x1), right (x2), top (y1) and bottom (y2).
    # for now since the centre of user and viewport frame is same: x1=x2, y1=y2
    x1 = int((w - vp_w)/2)
    x2 = x1
    y1 = int((h - vp_h)/2)
    y2 = y1

    corner_w = int(x1)
    corner_h = int(y1)

    cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter:v "crop=' + \
          str(vp_w)+':'+str(vp_h) + ':' + str(corner_w) + ':' + str(corner_h) + '" ' + output_yuv

    os.system(cmd)

    cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter:v "crop=' + \
          str(vp_w) + ':' + str(vp_h) + ':' + str(corner_w) + ':' + str(corner_h) + '" ' + output_png

    os.system(cmd)
