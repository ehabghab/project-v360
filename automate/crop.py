import os
import sys
import ast
if len(sys.argv) < 5:
    print('python3 crop.py viewport_centre_coordinate tiles_per_frame yuv_viewport_dir  yuv_output_dir')
    exit(1)


# Currently we are not using the viewport centre coordinate,
# assuming the centre of the viewport frame is same as center of user.
# But we need to use it at some point.
input_dir = sys.argv[3]

output_yuv_dir = sys.argv[4]

if os.path.isdir(input_dir):
    print('Correct Input')
else:
    print('Give correct input directory')
    exit(0)

if os.path.isdir(output_yuv_dir):
    print('Output yuv directory exists.')
else:
    os.mkdir(output_yuv_dir)


first_corr = {}
frame = 0
for line in open(sys.argv[2]).readlines():
    tiles = ast.literal_eval(line.split(":")[1])
    first_corr[frame] = {}
    first_corr[frame]["row"] = -1
    first_corr[frame]["col"] = -1
    
    # no overlap
    #tiles = [15,16,17,18,27,28,29,30,39,40,41,42]

    # yaw overlap
    #tiles = [25,26,27,33,34,35,36,37,38,39,45,46,47,48,49,50,51,57,58,59,60,61,62,63,69,70,71,72]
    
    # pitch overlap
    # tiles = [4,5,6,7,15,16,17,18,19,112,113,114,115,124,125,126,127,136,137,138,139]

    # pitch and yaw overlap
    #tiles = [1,2, 11, 12, 13,14,23,24,121,122,131,32,133,134,143,144]

    prev_row = -1
    prev_col = -1
    first_row_check = True
    for tile in sorted(tiles):
        row = int((tile - 1) / 12)
        col = ((tile - 1)  % 12)
        if prev_row != row and prev_row != -1:
            first_row_check = False
        if (first_corr[frame]["col"] == -1 or abs(prev_col - col) > 1) and first_row_check:
            first_corr[frame]["col"] = col
        if first_corr[frame]["row"] == -1 or  abs(prev_row - row) > 1:
            first_corr[frame]["row"] = row
        

        prev_col = col
        prev_row = row
    frame += 1


corner_crop = {}
frame = 0
deg_to_pix_yaw = (3840.0 / 360)
deg_to_pix_pitch = (1920.0 / 180)
for line in open(sys.argv[1]).readlines():
    corner_crop[frame] = {}
    first_col_corr = first_corr[frame]["col"] * 30
    first_row_corr = 180 - first_corr[frame]["row"] * 15
    yaw = int(float(line.split(",")[0]))
    pitch = int(float(line.split(",")[1]))

    if yaw < first_col_corr:
        yaw += 360
    
    if pitch > first_row_corr:
        pitch -= 180


    corner_crop[frame]["w"] = int(((yaw - first_col_corr) - 50) * deg_to_pix_yaw)
    corner_crop[frame]["h"] = int(((first_row_corr - pitch) - 50) * deg_to_pix_pitch)
    frame += 1


#Assuming the viewport is 100x100, for a 3840x1920 frame, the viewport comes to 1066x1066.
vp_h = 1066
vp_w = 1066
c = 0
for name in os.listdir(input_dir):
    file = input_dir + name
    # file = 'TestYUV/1_1280X1280.yuv'

    fname = file.split('/')[1]
    id = int(fname.split('_')[0]) - 1
    w = int(fname.split('_')[1].split('X')[0])
    h = int(fname.split('_')[1].split('X')[1].split('.')[0])
    output_yuv = output_yuv_dir + str(id) + '.yuv'

    cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter:v "crop=' + \
          str(vp_w)+':'+str(vp_h) + ':' + str(corner_crop[id]["w"]) + ':' + str(corner_crop[id]["h"]) + '" ' + output_yuv

    os.system(cmd)
    c += 1
for fi_c in range(0, c-1):
    os.system("cat "+output_yuv_dir+str(fi_c)+".yuv >> out.yuv")