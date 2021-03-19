import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import random
from collections import Counter

from pylab import arange, savefig, close, scatter, figure, plot, title
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


def CountFrequency(my_list):
	# Creating an empty dictionary
	freq = {}
	for item in my_list:
		if (item in freq):
			freq[item] += 1
		else:
			freq[item] = 1

	max = 0
	min = 1500
	for item in freq:
		if freq[item] > max:
			max = freq[item]
		if freq[item] < min:
			min = freq[item]

	for item in freq:
		freq[item] = ((freq[item] - min)/(max - min) * (4.5)) + 0.5

	return freq

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

	threshold_list = [0.25, 0.50, 0.75, 0.9]

	centreX = []
	centreY = []

	rectangles = []

	for threshold in threshold_list:

		for frame in range(0, len(results)):

			interest = results[frame] / np.amax(results[frame])
			z = interest > threshold

			# Show image of labeled clusters (shuffled)
			lw, num = measurements.label(z)
			area = measurements.sum(z, lw, index=arange(lw.max() + 1))
			areaImg = area[lw]

			# Bounding box
			sliced = measurements.find_objects(areaImg == areaImg.max())
			if (len(sliced) > 0):

				sliceX = sliced[0][1]
				sliceY = sliced[0][0]
				
				centreX.append((sliceX.start+sliceX.stop)/2)
				centreY.append((sliceY.start+sliceY.stop)/2)

				rectangles.append((sliceX.start, sliceY.start, sliceX.start, sliceY.stop, sliceX.stop, sliceY.stop, sliceX.stop, sliceY.start))


		centre_combos = list(zip(centreX, centreY))
		centre_weight_counter = Counter(centre_combos)
		centre_weights = [centre_weight_counter[(centreX[i], centreY[i])] for i, _ in enumerate(centreX)]

		figure(figsize=(5, 2.5))

		scatter(centreX, centreY, s=centre_weights, color= 'blue', marker='.')
		title("Threshold: " + str(threshold) + ' Tile: ' + str(360/tileHeight) + 'x' + str(360/tileWidth))
		savefig('scatterplot_cluster_centre' + '_' + str(threshold) + '.png')
		close()

		rectangleDict = CountFrequency(rectangles)

		figure(figsize=(5, 2.5))

		for rectangle in rectangleDict:
			rem = i%3
			if rem == 0:
				color = 'red'
			elif rem == 1:
				color = 'green'
			else:
				color = 'yellow'

			plot([rectangle[0], rectangle[2], rectangle[4], rectangle[6], rectangle[0]],
				 [rectangle[1], rectangle[3], rectangle[5], rectangle[7], rectangle[1]],
				 color=color, linewidth = rectangleDict[rectangle])

		title("Threshold: " + str(threshold) + ' Tile: ' + str(360/tileHeight) + 'x' + str(360/tileWidth))
		savefig('plot_cluster' + '_' + str(threshold) + '.png')
		scatter(centreX, centreY, s=centre_weights, color= 'blue', marker='.')

		title("Threshold: " + str(threshold) + ' Tile: ' + str(360/tileHeight) + 'x' + str(360/tileWidth))
		savefig('plot_all' + '_' + str(threshold) + '.png')
		close()

	print("Total users: ", len(video_data[args.video_id]))
if __name__ == "__main__":
	main()
