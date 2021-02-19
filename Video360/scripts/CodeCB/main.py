import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse


from helpers import *

parser = argparse.ArgumentParser()
parser.add_argument("--users", help="Number of users per video",
					type=int, default=1)
parser.add_argument("--height", help="Height of tile",
					type=int, default=30)
parser.add_argument("--width", help="Width of tile",
					type=int, default=60)
parser.add_argument("--heatmap", help="1: Heatmap X: Width, Y: Height of frame; 2: Heatmap X: Frame, Y: Tile",
					type=int, default=2)

args = parser.parse_args()

traces = '../Data/traces'

read_file_size = 0                  #Flag to control using size threshold or reading file size. (1 would need split data)
chunk_length = 1000                 #in milliseconds
tileWidth = args.width
tileHeight = args.height
total_frames = 1525
frames_per_chunk = 25

def main():

	data = get_data(traces, args.users)

	print("Generating tile map")
	tileMap = generateMAP(tileWidth, tileHeight)

	print("Getting data")
	results = getData(data, chunk_length, tileWidth, tileHeight, tileMap)

	watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV, wasted_area_in_watched_frame = results

	xaxis = 360 / tileWidth
	yaxis = 180 / tileHeight

	for video in watched_frames_in_tiles:

		print("Video: ", video)
		if args.heatmap == 1:
			base = np.zeros([int(xaxis)+1, int(yaxis)+1], dtype=int)
		elif args.heatmap == 2:
			base = np.zeros([int(xaxis*yaxis)+1,total_frames+1], dtype=int)
		for user in watched_frames_in_tiles[video]:
			print("Video: ", video, " User: ", user)
			for chunk in watched_frames_in_tiles[video][user]:
				print("Video: ", video, " User: ", user, " Chunk: ", chunk)
				for tile in watched_frames_in_tiles[video][user][chunk]:
					if args.heatmap == 1:
						x, y = degenerateMAP(tile, tileMap)
						x = int(x/tileWidth)
						y = int(y/tileHeight)
						base[y][x] += len(watched_frames_in_tiles[video][user][chunk][tile])
					elif args.heatmap == 2:
						for frame in watched_frames_in_tiles[video][user][chunk][tile]:
							base[tile][chunk*frames_per_chunk+frame] += 1

		plt.figure(figsize=(5,2.5))
		plt.margins(0, 0)
		plt.title('Heatmap of active regions in the video')

		ax = sns.heatmap(base)
		ax.invert_yaxis()

		if args.heatmap == 1:
			ax.set_xlabel('Width of a frame')
			ax.set_ylabel('Height of a frame')
			name = 'heatmap_1_tileheight_' + str(tileHeight) + '_tilewidth_' + str(tileWidth) + '_users_' + \
				   str(args.users) + '_videoID_' + str(video) + '.png'
		elif args.heatmap == 2:
			ax.set_xlabel('Frames in the video')
			ax.set_ylabel('Tiles in the frame')
			name = 'heatmap_2_tileheight_' + str(tileHeight) + '_tilewidth_' + str(tileWidth) + '_users_' + \
				   str(args.users) + '_videoID_' + str(video) + '.png'

		np.savetxt(name.replace(".png",".csv"),base, delimiter=",")

		fig = ax.get_figure()
		fig.savefig(name, bbox_inches='tight')
		fig.clf()
		plt.close()

if __name__ == "__main__":
	main()
