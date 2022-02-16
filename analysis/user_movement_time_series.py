import matplotlib.pyplot as plt
import numpy as np
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage Error: python3 user_movement_time_series.py <vp_coordinates>")
        sys.exit(1)
    res1 = open(sys.argv[1])
    yaw = []
    pitch = []
    frame_ids = []
    frame_id = 1
    for line in res1.readlines():
        data = line.split(',')
        frame_ids.append(frame_id)
        yaw.append(float(data[0]))
        pitch.append(float(data[1]))
        frame_id += 1

    yaw_diff = []
    pitch_diff = []

    degree_yaw = 3840/360.0
    degree_pitch = 1920/180.0
    for idx in range(1, len(yaw)):
        diff_yaw = yaw[idx] - yaw[idx - 1]
        diff_pitch = pitch[idx] - pitch[idx - 1]
        if diff_yaw > 180:  # overlapp left
            diff_yaw = diff_yaw - 360
        elif diff_yaw < -180:  # overlap right
            diff_yaw += 360

        if diff_pitch > 90:
            diff_pitch = diff_pitch - 180
        elif diff_pitch < -90:
            diff_pitch += 180

        yaw_diff.append(diff_yaw*degree_yaw)
        pitch_diff.append(diff_pitch*degree_pitch)

    colors = ['dodgerblue', 'seagreen', 'darkred']
    styles = ['-', '--', ':']
    plt.figure(figsize=(8, 4))
    plt.tight_layout()
    c = 0
    plt.plot(frame_ids[1:], yaw_diff, linewidth=2,
             color=colors[c], linestyle=styles[c], label="yaw")
    c += 1
    # plt.plot(frame_ids[1:], pitch_diff, linewidth=2,
    #         color=colors[c], linestyle=styles[c], label="pitch")
    c += 1

    plt.xticks(size=12)
    plt.yticks(size=12)
    plt.ylim(-80, 100)
    plt.legend(loc='best', prop={'size': 14, 'weight': 'bold'})
    plt.xlabel("Frame Id", size=14)
    plt.ylabel("Pixels difference", size=14)
    plt.savefig("user_movement.png", bbox_inches='tight', dpi=300)


# how often user change, how many tiles.
if __name__ == "__main__":
    main()
