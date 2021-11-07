import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import random

from pylab import figure, subplot, imshow, colorbar, title, arange, shuffle, plot, xlim, ylim, show, savefig, close
from scipy.ndimage import measurements
from helpers import *

parser = argparse.ArgumentParser()
parser.add_argument("--video_id", help="Video to be chosen",
					type=int, default=1)
parser.add_argument("--height", help="Height of tile",
					type=int, default=30)
parser.add_argument("--width", help="Width of tile",
					type=int, default=60)

args = parser.parse_args()

traces = '../Data/traces'

read_file_size = 0                  #Flag to control using size threshold or reading file size. (1 would need split data)
chunk_length = 1000                 #in milliseconds
tileWidth = args.width
tileHeight = args.height
total_frames = 1525
frames_per_chunk = 25

def main():

	video_data = {}
	data = get_data(traces, 100)
	video_data[args.video_id] = data[args.video_id]

	print("Generating tile map")
	tileMap = generateMAP(tileWidth, tileHeight)

	print("Getting data")
	results = getData(video_data, chunk_length, tileWidth, tileHeight, tileMap)

	watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV, wasted_area_in_watched_frame = results

	xaxis = 360 / tileWidth
	yaxis = 180 / tileHeight

	results = []

	for i in range(0, total_frames):
		temp = np.zeros([int(xaxis)+1, int(yaxis)+1], dtype=int)
		results.append(temp)

	for video in watched_frames_in_tiles:

		print("Video: ", video)

		for user in watched_frames_in_tiles[video]:
			print("Video: ", video, " User: ", user)
			for chunk in watched_frames_in_tiles[video][user]:
				print("Video: ", video, " User: ", user, " Chunk: ", chunk)
				for tile in watched_frames_in_tiles[video][user][chunk]:
					for frame in watched_frames_in_tiles[video][user][chunk][tile]:
						x, y = degenerateMAP(tile, tileMap)
						x = int(x / tileWidth)
						y = int(y / tileHeight)
						results[chunk*frames_per_chunk+frame][y][x] += 1

	threshold_list = [0.125, 0.50, 0.9]

	cluster_count = 'cluster_count'
	cluster_area = 'cluster_area'

	for threshold in threshold_list:

		ccn = (cluster_count + '_' + str(threshold))
		can = (cluster_area + '_' + str(threshold))

		cc = open(ccn + '.txt', 'a')
		ca = open(can + '.txt', 'a')

		for frame in range(0, len(results)):

			interest = results[frame]/np.amax(results[frame])

			z = interest > threshold

			figure(figsize=(16, 5))
			subplot(1, 3, 1)
			imshow(z, origin='lower', interpolation='nearest')
			colorbar()
			title("Matrix: Frame " + str(frame))

			# Show image of labeled clusters (shuffled)
			lw, num = measurements.label(z)

			line = str(frame) + ',' + str(num) + '\n'
			cc.write(line)

			subplot(1, 3, 2)

			b = arange(lw.max() + 1)  # create an array of values from 0 to lw.max() + 1
			shuffle(b)  # shuffle this array
			shuffledLw = b[lw]  # replace all values with values from b
			imshow(shuffledLw, origin='lower', interpolation='nearest')  # show image clusters as labeled by a shuffled lw
			colorbar()
			title("Labeled clusters")

			# Calculate areas
			subplot(1, 3, 3)
			area = measurements.sum(z, lw, index=arange(lw.max() + 1))
			areaImg = area[lw]
			im3 = imshow(areaImg, origin='lower', interpolation='nearest')
			colorbar()
			title("Clusters by area")

			line = str(frame) + ',' + str(area) + '\n'
			ca.write(line)

			# Bounding box
			sliced = measurements.find_objects(areaImg == areaImg.max())
			if (len(sliced) > 0):
				sliceX = sliced[0][1]
				sliceY = sliced[0][0]
				plotxlim = im3.axes.get_xlim()
				plotylim = im3.axes.get_ylim()
				plot([sliceX.start, sliceX.start, sliceX.stop, sliceX.stop, sliceX.start],
					 [sliceY.start, sliceY.stop, sliceY.stop, sliceY.start, sliceY.start],
					 color="red")
				xlim(plotxlim)
				ylim(plotylim)

			#show()
			savefig(ccn + '_' + str(frame) + '.png')
			close()

	for frame in range(0, len(results)):
		name = 'frame_' + str(frame) + '_video_' + str(args.video_id)

		plt.figure(figsize=(5, 2.5))
		plt.margins(0, 0)
		plt.title('Heatmap of ' + name)

		ax = sns.heatmap(results[frame])
		ax.invert_yaxis()

		ax.set_xlabel('Width of a frame')
		ax.set_ylabel('Height of a frame')

		fig = ax.get_figure()
		fig.savefig(name + '.png', bbox_inches='tight')
		fig.clf()
		plt.close()

	print("Total users: ", len(video_data[args.video_id]))
if __name__ == "__main__":
	main()
