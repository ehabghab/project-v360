import os
import sys
import ast
if len(sys.argv) < 5:
    print('python3 crop.py viewport_centre_coordinate tiles_per_frame yuv_dir_rebuffer yuv_dir_skip play_log_rebuffer  yuv_output_dir')
    exit(1)


# Currently we are not using the viewport centre coordinate,
# assuming the centre of the viewport frame is same as center of user.
# But we need to use it at some point.
input_dir_rebuffer = sys.argv[3]
input_dir_skip = sys.argv[4]
output_yuv_dir = sys.argv[6]

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


frames_to_stitch = []
frames_pts = []
crop_dim = {}
start_pts = 0
prev_pts = 0
for line in open(sys.argv[5],"r").readlines():
    if "frame" in line:
        continue
    data = line.split()
    frame_id = int(data[0])
    frame_pts = int(data[2])
    if start_pts == 0:
        start_pts = frame_pts
    # no rebuffering
    if frame_pts - prev_pts == 40 or prev_pts == 0:
        frame_path = (os.popen("ls "+input_dir_rebuffer+str(frame_id)+"_*").read()).replace("\n","")
        frames_to_stitch.append(frame_path)
        frames_pts.append(frame_pts - start_pts)
        crop_dim[frame_path] = {}
        crop_dim[frame_path]["w"] = corner_crop[frame_id-1]["w"]
        crop_dim[frame_path]["h"] = corner_crop[frame_id-1]["h"]
        
    else: # rebuffering
        frame_path_skip = (os.popen("ls "+input_dir_skip+str(frame_id)+"_*").read()).replace("\n","")
        frames_to_stitch.append(frame_path_skip)
        frames_pts.append((prev_pts + 40) - start_pts)
        crop_dim[frame_path_skip] = {}
        crop_dim[frame_path_skip]["w"] = corner_crop[frame_id-1]["w"]
        crop_dim[frame_path_skip]["h"] = corner_crop[frame_id-1]["h"]

        frame_path_rebuffer = (os.popen("ls "+input_dir_rebuffer+str(frame_id)+"_*").read()).replace("\n","")
        frames_to_stitch.append(frame_path_rebuffer)
        frames_pts.append(frame_pts - start_pts)
        crop_dim[frame_path_rebuffer] = {}
        crop_dim[frame_path_rebuffer]["w"] = corner_crop[frame_id-1]["w"]
        crop_dim[frame_path_rebuffer]["h"] = corner_crop[frame_id-1]["h"]

    prev_pts = frame_pts





#Assuming the viewport is 100x100, for a 3840x1920 frame, the viewport comes to 1066x1066.
vp_h = 1066
vp_w = 1066
c = 0
for frame in frames_to_stitch:
    frame_dim = frame.split("/")[len(frame.split("/")) - 1]
    w = int(frame_dim.split('_')[1].split('X')[0])
    h = int(frame_dim.split('_')[1].split('X')[1].split('.')[0])
    output_yuv = output_yuv_dir + str(c) + '.yuv'

    cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + frame + ' -filter:v "crop=' + \
          str(vp_w)+':'+str(vp_h) + ':' + str(crop_dim[frame]["w"]) + ':' + str(crop_dim[frame]["h"]) + '" ' + output_yuv
    os.system(cmd)
    c += 1

with open("frames_pts.txt","w") as fi:
    for pts in frames_pts:
        fi.write(str(pts)+"\n")

for fi_c in range(0, c-1):
    os.system("cat "+output_yuv_dir+str(fi_c)+".yuv >> out.yuv")