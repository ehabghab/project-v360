import os
import sys

if len(sys.argv) < 5:
    print('python3 moving_viewport.py yuv_viewport_dir viewport_centre_coordinate yuv_output_dir png_output_dir')

input_dir = sys.argv[1]
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

filenames = os.listdir(input_dir)

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

for name in filenames:

    f = int(name.split('_')[0])
    w = int(name.split('_')[1].split('X')[0])
    h = int(name.split('_')[1].split('X')[1].split('.')[0])

    output_yuv = ' ' + output_yuv_dir + str(f) + '.yuv'
    output_png = ' ' + output_png_dir + str(f) + '.png'

    y = centre[f]['yaw']
    p = centre[f]['pitch']

    left_gap = y - w/2
    right_gap = y + w/2 - 3840

    vp_top_corner_pitch = str(int(h/2))
    vp_top_corner_yaw = str(int(w/2))

    pitch_corner = str(y - int(h/2))
    yaw_corner = str(3840 - int(w))

    # ffmpeg -video_size 1280x1280 -i MahiMahiSystemYuv/1475_1280X1280.yuv -filter_complex
    # "[0:v] drawbox=color=red:t=10 [mark]; [mark] drawbox=x=630:y=630:w=20:h=20:color=red:t=max[test];
    # [test] split [test1] [test2] ; [test1] crop=572:1280:0:0, pad=572:1920:0:323:black[left];
    # [test2]crop=708:1280:572:0, pad=3268:1920:0:323:black[right]; [right][left] hstack" help1.png

    #Left margin
    #Cut left
    # cmd = 'ffmpeg -video_size ' + w + 'x' + h + ' -i ' \
    #       + frame + ' -filter:v "crop=' + str(int(abs(left_gap))) + ':' + h + ':0:0" 1475_left.yuv'
    # #Pad left
    # cmd = 'ffmpeg -video_size ' + str(int(abs(left_gap))) + 'x' + h + ' -i 1475_left.yuv -vf "pad=' + str(
    #     int(abs(left_gap))) + ':' + '1920' + ':0:' + pitch_corner + ':black" padded-black-left.yuv'
    # #Cut right
    # cmd = 'ffmpeg -video_size ' + w + 'x' + h + ' -i ' \
    #       + frame + ' -filter:v "crop=' + str(int(w) - int(abs(left_gap))) + ':' + h + ':' \
    #       + str(int(abs(left_gap))) + ':0" 1475_right.yuv'
    # #Pad right
    # cmd = 'ffmpeg -video_size ' + str(int(w) - int(abs(left_gap))) + 'x' + h + ' -i 1475_right.yuv -vf "pad=' + str(
    #     3840 - int(abs(left_gap))) + ':' + '1920' + ':0:' + pitch_corner + ':black" padded-black-right.yuv'

    if left_gap < 0:
        #Do something
        cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter_complex "[0:v]' +\
              ' drawbox=color=red:t=10 [mark]; [mark] drawbox=x=' + vp_top_corner_yaw + ':' + vp_top_corner_pitch + \
              'w=20:h=20:color=red:t=max[test]; [test] split [test1] [test2]; [test1] crop=' + str(int(abs(left_gap))) + \
              ':' + str(h) + ':0:0, pad=' + str(int(abs(left_gap))) + ':1920:0:' + pitch_corner + ':black[left];' + \
              '[test2]crop=' + str(int(w) - int(abs(left_gap))) + ':' + str(h) + ':' + str(int(abs(left_gap))) + ':0, pad=' + \
              str(3840 - int(abs(left_gap))) + ':' + '1920' + ':0:' + pitch_corner + \
              ':black[right]; [right][left] hstack, pad=3840:1920:0:0:black "' + \
              output_yuv

        os.system(cmd)

        cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter_complex "[0:v]' + \
              ' drawbox=color=red:t=10 [mark]; [mark] drawbox=x=' + vp_top_corner_yaw + ':' + vp_top_corner_pitch + \
              'w=20:h=20:color=red:t=max[test]; [test] split [test1] [test2]; [test1] crop=' + str(int(abs(left_gap))) + \
              ':' + str(h) + ':0:0, pad=' + str(int(abs(left_gap))) + ':1920:0:' + pitch_corner + ':black[left];' + \
              '[test2]crop=' + str(int(w) - int(abs(left_gap))) + ':' + str(h) + ':' + str(int(abs(left_gap))) + ':0, pad=' + \
              str(3840 - int(abs(left_gap))) + ':' + '1920' + ':0:' + pitch_corner + ':black[right]; [right][left] hstack "' + \
              output_png

        os.system(cmd)

    # Cut left
    # cmd = 'ffmpeg -video_size ' + w + 'x' + h + ' -i ' \
    #       + frame + ' -filter:v "crop=' + str(int(w) - int(abs(right_gap))) + ':' + h + ':0:0" 1473_left.yuv'
    #
    # # Pad left
    # cmd = 'ffmpeg -video_size ' + str(int(w) - int(abs(right_gap))) + 'x' + h + \
    #       ' -i 1473_left.yuv -vf "pad=' + str(3840 - int(abs(right_gap))) + ':' + \
    #       '1920' + ':' + yaw_corner + ':' + pitch_corner + ':black" padded-black-left.yuv'
    #
    # # Cut right
    # cmd = 'ffmpeg -video_size ' + w + 'x' + h + ' -i ' \
    #       + frame + ' -filter:v "crop=' + str(int(abs(right_gap))) + ':' + h + ':' \
    #       + str(int(abs(right_gap))) + ':0" 1473_right.yuv'
    #
    # #Pad right
    # cmd = 'ffmpeg -video_size ' + str(int(abs(right_gap))) + 'x' + h + \
    #       ' -i 1473_right.yuv -vf "pad=' + str(int(abs(right_gap))) + \
    #       ':' + '1920' + ':0:' + pitch_corner + ':black" padded-black-right.yuv'

    elif right_gap > 0:
        #Do something
        cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter_complex "[0:v]' + \
              ' drawbox=color=red:t=10 [mark]; [mark] drawbox=x=' + vp_top_corner_yaw + ':' + vp_top_corner_pitch + \
              'w=20:h=20:color=red:t=max[test]; [test] split [test1] [test2]; [test1] crop=' + str(int(w) - int(abs(right_gap))) + \
              ':' + str(h) + ':0:0, pad=' + str(3840 - int(abs(right_gap))) + ':1920:' + yaw_corner + ':' + \
              pitch_corner + ':black[left];' + '[test2]crop=' + str(int(abs(right_gap))) + ':' + str(h) + ':' + \
              str(int(abs(right_gap))) + ':0, pad=' + str(int(abs(right_gap))) + ':' + '1920' + ':0:' + \
              pitch_corner + ':black[right]; [right][left] hstack " ' + output_yuv

        os.system(cmd)

        cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter_complex "[0:v]' + \
              ' drawbox=color=red:t=10 [mark]; [mark] drawbox=x=' + vp_top_corner_yaw + ':' + vp_top_corner_pitch + \
              'w=20:h=20:color=red:t=max[test]; [test] split [test1] [test2]; [test1] crop=' + str(int(w) - int(abs(right_gap))) + \
              ':' + str(h) + ':0:0, pad=' + str(3840 - int(abs(right_gap))) + ':1920:' + yaw_corner + ':' + \
              pitch_corner + ':black[left];' + '[test2]crop=' + str(int(abs(right_gap))) + ':' + str(h) + ':' + \
              str(int(abs(right_gap))) + ':0, pad=' + str(int(abs(right_gap))) + ':' + '1920' + ':0:' + \
              pitch_corner + ':black[right]; [right][left] hstack " ' + output_png

        os.system(cmd)

    #ffmpeg -video_size 1280x1280 -i  MahiMahiSystemYuv/1473_1280X1280.yuv -filter_complex "[0:v]
    # drawbox=color=red:t=10 [mark]; [mark] drawbox=x=630:y=630:w=20:h=20:color=red:t=max,
    # pad=3840:1920:1249:329:black" test.png
    else:
        cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter_complex "[0:v]' + \
              ' drawbox=color=red:t=10 [mark]; [mark] drawbox=x=' + vp_top_corner_yaw + ':' + vp_top_corner_pitch + \
              ':w=20:h=20:color=red:t=max, pad=3840:1920:' + str(int(y - w/2)) + ':' + str(1920 - (p + h/2)) + \
              ':black" ' + output_yuv

        os.system(cmd)

        cmd = 'ffmpeg -video_size ' + str(w) + 'x' + str(h) + ' -i ' + input_dir + name + ' -filter_complex "[0:v]' + \
              ' drawbox=color=red:t=10 [mark]; [mark] drawbox=x=' + vp_top_corner_yaw + ':' + vp_top_corner_pitch + \
            ':w=20:h=20:color=red:t=max, pad=3840:1920:' + str(int(y - w / 2)) + ':' + str(1920 - int(p + h / 2)) + \
              ':black" ' + output_png

        os.system(cmd)



