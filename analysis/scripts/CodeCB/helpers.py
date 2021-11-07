import os
import math

FOV = 100
size_threshold = {'6x6': 1, '12x12': 1.07, '24x18': 1.22}  #this is the average frame size for chunk length of 1s [relative]


def get_data(traces, users):
	data = {}
	files = os.listdir(traces)

	for file in files:

		if '.csv' in file:
			fname = traces + '/' + file

			print("Filename: ", file)

			vID = int(file.split("vID_")[1].split("_")[0])
			uID = int(file.split("uID_")[1].split("_")[0])

			if data.get(vID) != None and (len(data[vID]) == users):
				continue
			elif data.get(vID) == None:
				data[vID] = {}

			data[vID][uID] = list()
			f = open(fname, 'r')

			for line in f.readlines():
				if "yaw" in line:
					continue
				temp = line.split(',')
				playbackTime = float(temp[0])
				x = float(temp[1])
				y = float(temp[2])
				z = float(temp[3])
				data[vID][uID].append([playbackTime, x, y, z])

	return data
def get_tile_frame_sizes_threshold(arg, tile_width, tile_height, chunk_length, size_threshold):

	if arg == 1:

		H = str(int(tile_height))
		W = str(int(tile_width))

		dir = "../split/Width" + W + "_Height" + H + "/"

		if chunk_length == 200:
			dir += "EXP4"
		elif chunk_length == 1000:
			dir += "EXP2"

		tile_frame_sizes = {} #key1 = tile, key2 = frameNum, value size
		count = 1
		for i in range(0,int(H)): #row
			for j in range(0,int(W)):
				tile_frame_sizes[count] = {} # new tile
				dirTile = dir+"/encoded_payloadExtract/"+str(i+1)+"_c_"+str(j+1)
				fList = os.listdir(dirTile)
				for f in fList:
					frame_num = int(f.split(".")[0])
					tile_frame_size = os.path.getsize(dirTile+"/"+f)
					tile_frame_sizes[count][frame_num] = tile_frame_size
				count +=1

		return tile_frame_sizes

	else:

		frame_sizes = {}

		for i in range(1,1501):
			frame_sizes[i] = 41070

		num_of_tiles = tile_width * tile_height * 1.

		tile_frame_sizes_w_threshold = {}
		for frame_num in frame_sizes:
			tile_frame_size = (frame_sizes[frame_num] / num_of_tiles) \
							  * size_threshold[str(int(tile_width))+"x"+str(int(tile_height))]
			for i in range(1,int(num_of_tiles)+1):
				if tile_frame_sizes_w_threshold.get(i) is None:
					tile_frame_sizes_w_threshold[i] = {}
				tile_frame_sizes_w_threshold[i][frame_num] = tile_frame_size

		return tile_frame_sizes_w_threshold

def generateMAP(tileWidth,tileHeight):
	map = {}
	blockNum = 1

	for y in range (180,0,-tileHeight):
		for x in range(0,360,tileWidth):
			if map.get(x,None) == None:
				map[x] = {}
			map[x][y]=blockNum
			blockNum += 1
	return map

def degenerateMAP(blockNum, map):

	for x in map:
		for y in map[x]:
			if map[x][y] == blockNum:
				return int(x), int(y)

def getTiles(map,cx,cy,tileWidth,tileHeight):

	offset = FOV/2.0

	x1 = cx - offset
	if (x1 < 0):
		x1 = 360 + x1
	x2 = cx + offset
	if (x2 > 360):
		x2 = x2 - 360

	x3 = x1
	x4 = x2
	y1 = cy - offset
	if (y1 < 0):
		y1 = 180 - (180 + y1)
		x3 = x1 + 180
		x4 = x2 + 180
		if x3 > 360:
			x3 = x3 - 360
		if x4 > 360:
			x4 = x4 - 360

	y2 = cy + offset
	x5 = x1
	x6 = x2
	if (y2 > 180):
		y2 = 180 - (y2 - 180)
		x5 = x1 + 180
		x6 = x2 + 180
		if x5 > 360:
			x5 = x5 - 360
		if x6 > 360:
			x6 = x6 - 360

	#up left x5,y2
	#up right x6,y2
	#down left x3,y1
	#down right x4,y1
	upflipped = False
	xul = int(x5/tileWidth) * tileWidth
	xur = math.ceil(x6/tileWidth) * tileWidth
	# up edges flipped
	if x5 != x1 and x6!= x2:
		upflipped = True
		yu = int(y2/tileHeight) * tileHeight
	else:
		yu = math.ceil(y2/tileHeight) * tileHeight

	downflipped = False
	xdl = int(x3/tileWidth) * tileWidth
	xdr = math.ceil(x4/tileWidth) * tileWidth
	# down edges flipped
	if x3 != x1 and x4 != x2:
		downflipped = True
		yd = math.ceil(y1/tileHeight) * tileHeight
	else:
		yd = int(y1/tileHeight) * tileHeight

	# flipped or not
	# xaxis are wrapped or not!
	tiles = set()

	if not upflipped and not downflipped:
		if xdl < xdr: #It is not wrapping around
			for j in range(int(yu),int(yd),-tileHeight):
				for i in range(int(xul),int(xur),tileWidth):
					tiles.add(map[i][j])
		else:
			for j in range(int(yu),int(yd),-tileHeight):
				for i in range(int(xul), 360, tileWidth):
					tiles.add(map[i][j])
				for i in range(0, int(xur), tileWidth):
					tiles.add(map[i][j])

	elif upflipped:
		#Tiles from lower coordinates to center
		#no overlapping on lower coordinates
		if xdl < xdr:
			for j in range(int(yd)+tileHeight,181,tileHeight):
				for i in range(int(xdl),int(xdr),tileWidth):
					tiles.add(map[i][j])
		#overlapping lower coordinates
		elif xdl > xdr:
			for j in range(int(yd)+tileHeight,181,tileHeight):
				for i in range(int(xdl),360,tileWidth):
					tiles.add(map[i][j])
				for i in range(0,int(xdr),tileWidth):
					tiles.add(map[i][j])

		#Tiles from upper coordinates from/to center
		#no overlapping on upper coordinates
		if xul < xur:
			for j in range(int(yu)+tileHeight,181,tileHeight):
				for i in range(int(xul),int(xur),tileWidth):
					tiles.add(map[i][j])
		# overlapping upper coordinates
		elif xul > xur:
			for j in range(int(yu)+tileHeight,181,tileHeight):
				for i in range(int(xul),360,tileWidth):
					tiles.add(map[i][j])
				for i in range(0,int(xur),tileWidth):
					tiles.add(map[i][j])

		if xul > xur and xdl > xdr:
			print ("Error: overlapping upper and lower coordinates")

	elif downflipped:
		if xul < xur:
			for j in range(int(yu),0,-tileHeight):
				for i in range(int(xul),int(xur),tileWidth):
					tiles.add(map[i][j])
		elif xul > xur:
			for j in range(int(yu),0,-tileHeight):
				for i in range(int(xul),360,tileWidth):
					tiles.add(map[i][j])
				for i in range(0,int(xur),tileWidth):
					tiles.add(map[i][j])

		if xdl < xdr:
			for j in range(int(yd),0,-tileHeight):
				for i in range(int(xdl),int(xdr),tileWidth):
					tiles.add(map[i][j])
		elif xdl > xdr:
			for j in range(int(yd),0,-tileHeight):
				for i in range(int(xdl),360,tileWidth):
					tiles.add(map[i][j])
				for i in range(0,int(xdr),tileWidth):
					tiles.add(map[i][j])


		if xul > xur and xdl > xdr:
			print ("Error: overlapping upper and lower coordinates")


	tileAreaUsed = {} # how much used from tiles at edgs
	if not upflipped and not downflipped:
		for i in range (int(yu),int(yd)+1,-tileHeight):
			wLeft = xul + tileWidth - x5
			wRight = x6 - (xur - tileWidth)
			if i == yu:
				l = y2 - (i - tileHeight)
			elif i == yd+tileHeight:
				l = i - y1
			else:
				l = tileHeight
			tileAreaUsed[map[xul][i]] = wLeft * l
			tileAreaUsed[map[xur-tileWidth][i]] = wRight * l
		if xul < xur: #no overlapping
			for i in range(int(xul+ tileWidth), int(xur-tileWidth),tileWidth):
				w = tileWidth
				lu = y2 -(yu - tileHeight)
				ld = (yd + tileHeight) - y1
				tileAreaUsed[map[i][yu]] = w * lu
				tileAreaUsed[map[i][yd+tileHeight]] = w * ld
		else:
			for i in range(int(xul+ tileWidth), 360,tileWidth):
				w = tileWidth
				lu = y2 -(yu - tileHeight)
				ld = (yd + tileHeight) - y1
				tileAreaUsed[map[i][yu]] = w * lu
				tileAreaUsed[map[i][yd+tileHeight]] = w * ld

			for i in range(0,int(xur-tileWidth),tileWidth):
				w = tileWidth
				lu = y2 -(yu - tileHeight)
				ld = (yd + tileHeight) - y1
				tileAreaUsed[map[i][yu]] = w * lu
				tileAreaUsed[map[i][yd+tileHeight]] = w * ld

	elif upflipped:
		for i in range (180,int(yd),-tileHeight):
			wLeft = xdl + tileWidth - x3
			wRight = x4 - (xdr - tileWidth)
			if i == yd+tileHeight:
				l = i - y1
			else:
				l = tileHeight
			tileAreaUsed[map[xdl][i]] = wLeft * l
			tileAreaUsed[map[xdr-tileWidth][i]] = wRight * l

		for i in range (180,int(yu),-tileHeight):
			wLeft = xul + tileWidth - x5
			wRight = x6 - (xur - tileWidth)
			if i == yu+tileHeight:
				l = i - y2
			else:
				l = tileHeight
			tileAreaUsed[map[xul][i]] = wLeft * l
			tileAreaUsed[map[xur-tileWidth][i]] = wRight * l

		if xdl < xdr:
			for i in range(int(xdl+ tileWidth), int(xdr-tileWidth),tileWidth):
				w = tileWidth
				ld = (yd + tileHeight) - y1
				tileAreaUsed[map[i][yd+tileHeight]] = w * ld

		elif xdl >xdr:
			for i in range(int(xdl+ tileWidth), 360,tileWidth):
				w = tileWidth
				ld = (yd + tileHeight) - y1
				tileAreaUsed[map[i][yd+tileHeight]] = w * ld
			for i in range(0, int(xdr-tileWidth),tileWidth):
				w = tileWidth
				ld = (yd + tileHeight) - y1
				tileAreaUsed[map[i][yd+tileHeight]] = w * ld

		if xul < xur:
			for i in range(int(xul+ tileWidth), int(xur-tileWidth),tileWidth):
				w = tileWidth
				ld = (yu + tileHeight) - y2
				tileAreaUsed[map[i][yu+tileHeight]] = w * ld

		elif xul >xur:
			for i in range(int(xul+ tileWidth), 360,tileWidth):
				w = tileWidth
				ld = (yu + tileHeight) - y2
				tileAreaUsed[map[i][yu+tileHeight]] = w * ld
			for i in range(0, int(xur-tileWidth),tileWidth):
				w = tileWidth
				ld = (yu + tileHeight) - y2
				tileAreaUsed[map[i][yu+tileHeight]] = w * ld

	elif downflipped :
		for i in range (int(yd),0,-tileHeight):
			wLeft = xdl + tileWidth - x3
			wRight = x4 - (xdr - tileWidth)
			if i == yd:
				l = y1 - (i - tileHeight)
			else:
				l = tileHeight
			tileAreaUsed[map[xdl][i]] = wLeft * l
			tileAreaUsed[map[xdr-tileWidth][i]] = wRight * l

		for i in range (int(yu),0,-tileHeight):
			wLeft = xul + tileWidth - x5
			wRight = x6 - (xur - tileWidth)
			if i == yu:
				l = y2 - (i - tileHeight)
			else:
				l = tileHeight
			tileAreaUsed[map[xul][i]] = wLeft * l
			tileAreaUsed[map[xur-tileWidth][i]] = wRight * l

		if xdl < xdr:
			for i in range(int(xdl+ tileWidth), int(xdr-tileWidth),tileWidth):
				w = tileWidth
				ld = y1 - (yd - tileHeight)
				tileAreaUsed[map[i][yd]] = w * ld

		elif xdl > xdr:
			for i in range(int(xdl+ tileWidth), 360,tileWidth):
				w = tileWidth
				ld = y1 - (yd - tileHeight)
				tileAreaUsed[map[i][yd]] = w * ld
			for i in range(0, int(xdr-tileWidth),tileWidth):
				w = tileWidth
				ld = y1 - (yd - tileHeight)
				tileAreaUsed[map[i][yd]] = w * ld

		if xul < xur:
			for i in range(int(xul+ tileWidth), int(xur-tileWidth),tileWidth):
				w = tileWidth
				ld = y2 - (yu - tileHeight)
				tileAreaUsed[map[i][yu]] = w * ld

		elif xul >xur:
			for i in range(int(xul+ tileWidth), 360,tileWidth):
				w = tileWidth
				ld = y2 - (yu - tileHeight)
				tileAreaUsed[map[i][yu]] = w * ld
			for i in range(0, int(xur-tileWidth),tileWidth):
				w = tileWidth
				ld = y2 - (yu - tileHeight)
				tileAreaUsed[map[i][yu]] = w * ld

	tileWastedArea = {}
	for tile in tileAreaUsed:
		tileWastedArea[tile] = (tileWidth*tileHeight) - tileAreaUsed[tile]

	return tiles,tileWastedArea

def getData(data, chunkLength, tileWidth, tileHeight, tileMap):

	watched_frames_in_tiles = {}  # frames watched within tile. key is (user id --> sec -->tile), value number of frames.
	num_frames_in_tile = {}  # index of watched frames in chunk, key is (user id --> chunkNum), value list of frames number within tile.
	num_tiles_in_FOV = {}  # number of tiles in a single FOV
	wasted_area_in_watched_frame = {}

	for vID in data:

		print("Getting data for vID: ", vID)
		watched_frames_in_tiles[vID] = {}
		num_frames_in_tile[vID] = {}
		num_tiles_in_FOV[vID] = {}
		wasted_area_in_watched_frame[vID] = {}

		for uID in data[vID]:

			FOVNum = 1  # number of frames in second (frame counter)
			startTime = -1
			prevFrameTime = 0
			chunkID = -1

			watched_frames_in_tiles[vID][uID] = {}
			num_frames_in_tile[vID][uID] = {}
			num_tiles_in_FOV[vID][uID] = {}
			wasted_area_in_watched_frame[vID][uID] = {}

			for row in data[vID][uID]:

				timestamp = row[0]  # sec.msec
				yaw = math.degrees(row[1]) + 180
				pitch = math.degrees(row[2]) + 90
				roll = math.degrees(row[3])

				if startTime == -1:  # first frame in first chunk of the video.

					startTime = timestamp * 1000
					chunkID = 0
					FOVNum = 1

				timestampCal = timestamp * 1000 - startTime  # calibrate the time to start from zero.

				# if we moved to next chunk in video
				if timestampCal >= chunkID * chunkLength + chunkLength:

					chunkID += 1
					FOVNum = 1

				# frames are 40msec apart (25FPS).
				if (timestampCal - prevFrameTime) >= 40 or prevFrameTime == 0:
					prevFrameTime += 40
					tiles, wastage = getTiles(tileMap, yaw, pitch, tileWidth, tileHeight)
					# The function gives the watched tiles in a frame and the wastage associated [in area]

					if watched_frames_in_tiles[vID][uID].get(chunkID, None) == None:
						watched_frames_in_tiles[vID][uID][chunkID] = {}
						wasted_area_in_watched_frame[vID][uID][chunkID] = {}

					num_tiles_in_FOV[vID][uID][chunkID] = {}
					num_tiles_in_FOV[vID][uID][chunkID][FOVNum] = len(tiles)
					# to calcuate the total area requested (GRAY AREA)
					# track frames in tile which have been watched by user.

					for tile in tiles:
						if watched_frames_in_tiles[vID][uID][chunkID].get(tile, None) == None:
							watched_frames_in_tiles[vID][uID][chunkID][tile] = list()
						watched_frames_in_tiles[vID][uID][chunkID][tile].append(FOVNum)

					# for each frame watched in a tile what was the area used.
					for tile in wastage:
						if wasted_area_in_watched_frame[vID][uID][chunkID].get(tile, None) == None:
							wasted_area_in_watched_frame[vID][uID][chunkID][tile] = {}
						wasted_area_in_watched_frame[vID][uID][chunkID][tile][FOVNum] = wastage[tile]

					# the FPS for that second.
					num_frames_in_tile[vID][uID][chunkID] = FOVNum
					FOVNum += 1

	return watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV, wasted_area_in_watched_frame

def getWaste(watched_frames_in_tiles, wasted_area_in_watched_frame, num_frames_in_tile, tileFrameSizes,chunkLength,tileWidth,tileHeight):

	IPerSec = int(round(1000.0/chunkLength)) #number of I-frames in a sec.
	IFrameDist = int(round(25.0/IPerSec)) # Distance between two I-frames

	waste = {}
	area_waste = {}
	drop_frame_waste = {}
	total_bytes = {}

	for uID in watched_frames_in_tiles:

		waste[uID] = {}
		area_waste[uID] = {}
		drop_frame_waste[uID] = {}
		total_bytes[uID] = {}
		baseFrameNum = 0

		for chunkID in watched_frames_in_tiles[uID]:

			waste[uID][chunkID] = 0
			area_waste[uID][chunkID] = 0
			drop_frame_waste[uID][chunkID] = 0
			total_bytes[uID][chunkID] = 0
			dropped_frames_in_tiles = 0 # total number of wasted frames in a chunk
			wastedAreInTileFrames = 0

			if chunkID % IPerSec == 0:
				baseFrameNum = ((chunkID/IPerSec)*25)
			else:
				baseFrameNum += IFrameDist

			#print(baseFrameNum)
				#size of un-watched frames in all tiles.

			for tile in watched_frames_in_tiles[uID][chunkID]:
				for fId in range(1,num_frames_in_tile[uID][chunkID]+1): #loop over all frames ids in tile.

					if tileFrameSizes[tile].get(baseFrameNum+fId,None) != None:# if we have the size of it (rare cases where this is maybe false)
						total_bytes[uID][chunkID] += tileFrameSizes[tile][baseFrameNum+fId] # size of all frames in tile watched and unwatched.


					if fId not in watched_frames_in_tiles[uID][chunkID][tile]:# if frame id not the watched subset.
						if tileFrameSizes[tile].get(baseFrameNum+fId,None) != None:# if we have the size of it (rare cases where this is maybe false)
							dropped_frames_in_tiles += tileFrameSizes[tile][baseFrameNum+fId]



			for tile in wasted_area_in_watched_frame[uID][chunkID]:
				for fovNum in wasted_area_in_watched_frame[uID][chunkID][tile]:
					if tileFrameSizes[tile].get(baseFrameNum+fovNum,None) != None:
						tileframeSize = tileFrameSizes[tile][baseFrameNum+fovNum]
						extraArea = wasted_area_in_watched_frame[uID][chunkID][tile][fovNum]
						wastedAreInTileFrames += tileframeSize * (extraArea/(tileWidth*tileHeight))
			area_waste[uID][chunkID] =  wastedAreInTileFrames
			drop_frame_waste[uID][chunkID] = dropped_frames_in_tiles
			waste[uID][chunkID] = dropped_frames_in_tiles + wastedAreInTileFrames
	return area_waste, drop_frame_waste,waste,total_bytes