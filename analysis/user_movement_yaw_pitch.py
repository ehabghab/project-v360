import sys
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times",
    "font.sans-serif": ["Times"]})


def main():

    if len(sys.argv) < 2:
        print(
            "ERROR: python QoE.py <usr_vp_corr>")
        sys.exit(1)
    yaws = []
    pitches = []
    x_axis = []
    frm_id = 1
    for line in open(sys.argv[1]).readlines():
        data = line.split(",")
        yaws.append(float(data[0]))
        pitches.append(float(data[1]))
        x_axis.append(frm_id)
        frm_id += 1
    yaws = yaws[:-25]
    pitches = pitches[:-25]
    x_axis = x_axis[:-25]

    plt.figure(figsize=(6, 2))
    plt.tight_layout()
    plt.plot(x_axis, yaws, linewidth=2,
             linestyle="-", color="dodgerblue", label="Yaw")

    plt.plot(x_axis, pitches, linewidth=2,
             linestyle=":", color="seagreen", label="Pitch")

    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.legend(loc='upper left', prop={'size': 10,
               'weight': 'bold'}, edgecolor="black")
    plt.ylabel('Movement degree', size=12)
    plt.xlabel('Frame id', size=12)
    # plt.ylim(.93,1.01)
    # plt.xlim(-1,10)
    # plt.show()
    plt.savefig("user_movement_yaw_pitch.png", bbox_inches='tight', dpi=300)


if __name__ == "__main__":
    main()
