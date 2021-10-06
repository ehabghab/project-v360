
from numpy.lib.function_base import median
from pyquaternion import Quaternion
import math
import matplotlib.pyplot as plt
import numpy as np
from os import walk
import os
import matplotlib.patches as mpatches
import    faulthandler
import sys
from collections import OrderedDict

FOV = 100
linestyles = OrderedDict(
		[('solid',               (0, ())),
		('loosely dotted',      (0, (1, 10))),
		('dotted',              (0, (1, 5))),
		('densely dotted',      (0, (1, 1))),

		('loosely dashed',      (0, (5, 10))),
		('dashed',              (0, (5, 5))),
		('densely dashed',      (0, (5, 1))),

		('loosely dashdotted',  (0, (3, 10, 1, 10))),
		('dashdotted',          (0, (3, 5, 1, 5))),
		('densely dashdotted',  (0, (3, 1, 1, 1))),

		('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
		('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
		('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))])

def modifybox(boxplot,data,whis=None,linewidth=None,color=None,medianColor=None,style=None):


	q1=np.percentile(data,10)
	q2=np.percentile(data,25)
	q3=np.percentile(data,50)
	q4=np.percentile(data,75)
	q5=np.percentile(data,90)
	if whis!=None:
		q1=np.percentile(data,whis[0])
		q5=np.percentile(data,whis[1])

	boxplot['whiskers'][0].set_ydata([q1,q2])
	boxplot['caps'][0].set_ydata([q1,q1])
	#boxplot['boxes'][0].set_ydata([q2,q2,q4,q4,q2])
	boxplot['medians'][0].set_ydata([q3,q3])
	boxplot['caps'][1].set_ydata([q5,q5])
	boxplot['whiskers'][1].set_ydata([q4,q5])

	if linewidth==None:
		linewidth=1

	if medianColor==None:
		medianColor='r'
	for cap in boxplot['caps']:
		cap.set(linewidth=linewidth,color=color)
	for cap in boxplot['boxes']:
		cap.set(linewidth=linewidth, hatch=style)
	for cap in boxplot['whiskers']:
		cap.set(linewidth=linewidth,color=color)
	for cap in boxplot['medians']:
		cap.set(linewidth=linewidth,color=medianColor)


	return q5

def plotMap(tileMap,cx,cy,tileWidth,tileHeight):
	f = plt.figure(figsize=(12,6))
	ax = f.add_subplot(111)

	for y in range (180,0,-tileHeight):
		for x in range (0,360,tileWidth):
			xaxis = x+(tileWidth /2)

			yaxis = y-(tileHeight/2)

			plt.text(xaxis,yaxis,str(tileMap[x][y]),horizontalalignment='center', verticalalignment='center',fontsize=10)
	minor_ticks = np.arange(0, 361, tileWidth)
	plt.xticks(minor_ticks)

	ax.set_xticks(minor_ticks, minor=True)
	minor_ticks = np.arange(0, 181, tileHeight)
	plt.yticks(minor_ticks)

	ax.set_yticks(minor_ticks, minor=True)
	ax.set_xlabel('Yaw')
	ax.set_ylabel('Pitch')

	# And a corresponding grid
	ax.grid(which='both')
	plt.grid()
	plt.xlim(0,360,tileWidth)
	plt.ylim(0,180)
	plt.scatter(cx,cy,linewidth='8',marker='x',color='r')
	offset = FOV/2.0

	x1 = cx - offset
	if (x1 < 0):
		x1 = 360 + x1
	x2 = cx + offset
	if (x2 >= 360):
		x2 = x2 - 360



	x3 = x1
	x4 = x2
	y1 = cy - offset
	if (y1 < 0):
		y1 = 180 - (180 + y1)
		x3 = x1 + 180
		x4 = x2 + 180
		if x3 >= 360:
			x3 = x3 - 360
		if x4 >= 360:
			x4 = x4 - 360



	y2 = cy + offset
	x5 = x1
	x6 = x2
	if (y2 >= 180):
		y2 = 180 - (y2 - 180)
		x5 = x1 + 180
		x6 = x2 + 180
		if x5 >= 360:
			x5 = x5 - 360
		if x6 >= 360:
			x6 = x6 - 360
	faulthandler.enable()
	plt.scatter(x3,y1, color = 'g',linewidth = '3',marker = '^' if x3 == x1 else "v")
	plt.scatter(x5,y2, color = 'r',linewidth = '3',marker = 'v' if x5 ==x1 else "^")
	plt.scatter(x4,y1, color = 'g',linewidth = '3', marker = '^' if x4 == x2 else "v")
	plt.scatter(x6,y2, color = 'r',linewidth = '3', marker = 'v' if x6 ==x2 else "^")
	plt.show()

def getTiles(map,cx,cy,tileWidth,tileHeight):

	offset = FOV/2.0

	x1 = cx - offset
	if (x1 < 0):
		x1 = 360 + x1
	x2 = cx + offset
	if (x2 > 360):
		x2 = x2 - 360
	elif (x2 == 360):
		x2 = 359



	x3 = x1
	x4 = x2
	y1 = cy - offset
	if (y1 < 0):
		y1 = 180 - (180 + y1)
		x3 = x1 + 180
		x4 = x2 + 180
		if x3 > 360:
			x3 = x3 - 360
		elif (x3 == 360):
			x3 = 359
		if x4 > 360:
			x4 = x4 - 360
		elif (x4 == 360):
			x4 = 359



	y2 = cy + offset
	x5 = x1
	x6 = x2
	if (y2 > 180):
		y2 = 180 - (y2 - 180)
		x5 = x1 + 180
		x6 = x2 + 180
		if x5 > 360:
			x5 = x5 - 360
		elif (x5 == 360):
			x5 = 359

		if x6 > 360:
			x6 = x6 - 360
		elif (x6 == 360):
			x6 = 359



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

	#print "("+str(xul)+","+str(yu)+")"
	#print "("+str(xur)+","+str(yu)+")"
	#print "("+str(xdl)+","+str(yd)+")"
	#print "("+str(xdr)+","+str(yd)+")"
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


	# get the wasted area
	tileWastedArea = {}
	for tile in tileAreaUsed:
		tileWastedArea[tile] = (tileWidth*tileHeight) - tileAreaUsed[tile]

	return tiles,tileWastedArea

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

def get_tile_frame_sizes(tile_width,tile_height,chunk_length):
	if chunk_length == 200:
		dir = "../split/Width"+str(tile_width)+"_Height"+str(tile_height)+"/EXP4"
	elif chunk_length == 1000:
		dir = "../split/Width"+str(tile_width)+"_Height"+str(tile_height)+"/EXP2"

	tile_frame_sizes = {} #key1 = tile, key2 = frameNum, value size
	count = 1
	for i in range(0,tile_height): #row
		for j in range(0,tile_width):
			tile_frame_sizes[count] = {} # new tile
			dirTile = dir+"/encoded_payloadExtract/"+str(i+1)+"_c_"+str(j+1)
			fList = os.listdir(dirTile)
			for f in fList:
				frame_num = int(f.split(".")[0])
				tile_frame_size = os.path.getsize(dirTile+"/"+f)
				tile_frame_sizes[count][frame_num] = tile_frame_size
			count +=1

	return tile_frame_sizes

def get_tile_frame_sizes_threshold(tile_width,tile_height,chunk_length,size_threshold):
	'''
		scheme, chunk length, avg frame size
		6X6,	1000,	41069.216			(1.00X)
		12X12,	1000,	43643.12			(1.06X)
		24X18,	1000,	50023.6653333		(1.18X)
		6X6,	200,	83872.566			(2.04X)					
		12X12,	200,	87577.0086667		(2.13X)
		24X18,	200,	98263.8193333		(2.39X)
	'''
	'''
		6x6,	500, 	xxxx				(1.07)
		12x12,	500,	xxxx				(1.13)
		24x18,	500,	xxxx				(1.26)
	'''
	dir = "../split/Width6_Height6/EXP4"
	tile_frame_sizes = {} #key1 = tile, key2 = frameNum, value size
	count = 1
	for i in range(0,6): #row
		for j in range(0,6):
			tile_frame_sizes[count] = {} # new tile
			dirTile = dir+"/encoded_payloadExtract/"+str(i+1)+"_c_"+str(j+1)
			fList = os.listdir(dirTile)
			for f in fList:
				frame_num = int(f.split(".")[0])
				tile_frame_size = os.path.getsize(dirTile+"/"+f)
				tile_frame_sizes[count][frame_num] = tile_frame_size
			count +=1



	frame_sizes = {} #get the 6x6 frame size.
	for tile in tile_frame_sizes:
		for frame_num in tile_frame_sizes[tile]:
			if frame_sizes.get(frame_num) is None:
				frame_sizes[frame_num] = 0
			frame_sizes[frame_num] = 41070# avg 6x6 frame size.

	num_of_tiles = tile_width * tile_height * 1.

	tile_frame_sizes_w_threshold = {}
	for frame_num in frame_sizes:
		tile_frame_size = (frame_sizes[frame_num] / num_of_tiles) \
							* size_threshold[str(int(tile_width))+"x"+str(int(tile_height))\
								+"_"+str(chunk_length)]
		for i in range(1,int(num_of_tiles)+1):
				if tile_frame_sizes_w_threshold.get(i) is None:
					tile_frame_sizes_w_threshold[i] = {}
				tile_frame_sizes_w_threshold[i][frame_num] = tile_frame_size
	return tile_frame_sizes_w_threshold

def yawMovement(yaw,prevYaw,startYaw,left,right,flip):

	moveRight = yaw - prevYaw #positive if moving to right or neg in case of overlapping.
	moveLeft = prevYaw - yaw  #positive if moving to the left or neg in case of overlapping.

	#if there is an overlapping the comparison to the start is going to be flipped as well.
	if moveRight > 0 and moveRight <= 180: #move to the right no overlapping.
		True
	elif moveRight <= -180: #move to the right overlapping. if it is -179, it could be just turn to the left.
		flip = not flip
	elif moveLeft > 0 and moveLeft <= 180: #move to the left no overlapping
		True
	elif moveLeft <= -180: #move to the left overlapping.
		flip = not flip
	elif moveLeft ==0 and moveRight ==0: #still on the x-axis.
		True
	else:
		print("uncovered case!")

	if flip:
		if yaw > startYaw:
			mL = startYaw + (360 - yaw)
			if mL > left:
				left = mL
		else:
			mR = (360 - startYaw) + yaw
			if mR > right:
				right = mR
	else:
		if yaw > startYaw:
			mR = yaw - startYaw
			if mR > right:
				right = mR
		else:
			mL = startYaw - yaw
			if mL > left:
				left = mL

	return left,right,flip

def pitchMovement(pitch,prevPitch,startPitch,up,down,flipVertical):

	moveUp = pitch - prevPitch #positive if moving to up or neg in case of overlapping.
	moveDown = prevPitch - pitch  #positive if moving to the left or neg in case of overlapping.
	#if there is an overlapping the comparison to the start is going to be flipped as well.
	if moveUp > 0 and moveUp <= 90: #move up no overlapping.
		True#print("move to the right.")
	elif moveUp < 0 and moveUp <= -90: #move up overlapping.
		#print("move up OVERLAPPED.")
		flipVertical = not flipVertical
	elif moveDown > 0 and moveDown <= 90: #move down no overlapping
		True#print("move to the left.")
	elif moveDown < 0 and moveDown <= -90: #move down overlapping.
		#print("move down OVERLAPPED.")
		flipVertical = not flipVertical
	elif moveDown ==0 and moveUp ==0: #still on the y-axis.
		True#print("no movement.")
	else: #Error
		print("uncovered case!")

	if flipVertical:
		if pitch > startPitch:
			mD = startPitch + (180 - pitch)
			if mD > down:
				down = mD
		else:
			mU = (180 - startPitch) + pitch
			if mU > up:
				up = mU
	else:
		if pitch > startPitch:
			mU = pitch - startPitch
			if mU > up:
				up = mU
		else:
			mD = startPitch - pitch
			if mD > down:
				down = mD

	return down,up,flipVertical

def calculateDis(rows,chunk_length):
	displacements = {}
	startTime = -1
	prevFrameTime = 0
	frameNum = 0
	l = list()
	for row in rows:
		timestamp = row[0]      #sec.msec
		yaw = math.degrees(row[1]) + 180
		pitch = math.degrees(row[2]) + 90
		roll = math.degrees(row[3])
		if startTime == -1: #first frame in first chunk of the video.
			startTime = timestamp * 1000
			chunkId = 0
		timestampCal = timestamp*1000 - startTime #calibrate the time to start from zero.

		if timestampCal >= chunkId*chunk_length + chunk_length:
			chunkId +=1


		if (timestampCal - prevFrameTime) >=40 or prevFrameTime == 0:
			prevFrameTime += 40
			frameNum +=1
			#print str(chunkId)+"->"+str(yaw)+","+str(pitch)

			if chunkId not in l:
				#print "====="
				displacements[chunkId] = {}
				displacements[chunkId]['left'] = 0
				displacements[chunkId]['right'] = 0
				displacements[chunkId]['up'] = 0
				displacements[chunkId]['down'] = 0
				displacements[chunkId]['yaw'] = yaw
				displacements[chunkId]['pitch'] = pitch
				l.append(chunkId)
				startYaw = yaw
				startPitch = pitch
				prevYaw = yaw
				prevPitch = pitch
				left = 0
				right = 0
				up = 0
				down = 0
				flipHorizantal = False
				flipVertical = False
				continue
			else:
				left,right,flipHorizantal = yawMovement(yaw,prevYaw,startYaw,left,right,flipHorizantal)
				down,up,flipVertical = pitchMovement(pitch,prevPitch,startPitch,up,down,flipVertical)
				prevYaw = yaw
				prevPitch = pitch
				displacements[chunkId]['left'] = left
				displacements[chunkId]['right'] = right
				displacements[chunkId]['up'] = up
				displacements[chunkId]['down'] = down

	return displacements

def getData(data,video,chunkLength,tileWidth,tileHeight,tileMap):
	watched_frames_in_tiles = {} # frames watched within tile. key is (user id --> sec -->tile), value number of frames.
	num_frames_in_tile = {} # index of watched frames in chunk, key is (user id --> chunkNum), value list of frames number within tile.
	num_tiles_in_FOV = {} # number of tiles in a single FOV
	wasted_area_in_watched_frame = {}

	for vID in data:
		if vID != video:
			continue
		for uID in data[vID]:
			FOVNum = 1 #number of frames in second (frame counter)
			startTime = -1
			prevFrameTime = 0
			chunkID = -1
			watched_frames_in_tiles[uID] = {}
			num_frames_in_tile[uID] = {}
			num_tiles_in_FOV[uID] = {}
			wasted_area_in_watched_frame[uID] = {}
			for row in data[vID][uID]:
				timestamp = row[0]      #sec.msec
				yaw = math.degrees(row[1]) + 180
				pitch = math.degrees(row[2]) + 90
				roll = math.degrees(row[3])
				if startTime == -1: #first frame in first chunk of the video.
					startTime = timestamp * 1000
					chunkID = 0
					FOVNum = 1

				timestampCal = timestamp*1000 - startTime #calibrate the time to start from zero.

				# if we moved to next chunk in video
				if timestampCal >= chunkID*chunkLength + chunkLength:
					chunkID +=1
					FOVNum = 1

				#frames are 40msec apart (25FPS).
				if (timestampCal - prevFrameTime) >=40 or prevFrameTime == 0:
					prevFrameTime += 40
					tiles,wastage = getTiles(tileMap,yaw,pitch,tileWidth,tileHeight)

					if  watched_frames_in_tiles[uID].get(chunkID,None) == None:
						watched_frames_in_tiles[uID][chunkID] = {}
						wasted_area_in_watched_frame[uID][chunkID] = {}
					num_tiles_in_FOV[uID][chunkID] = {}

					num_tiles_in_FOV[uID][chunkID][FOVNum] = len(tiles) #to calcuate the total area requested (GRAY AREA)
					# track frames in tile which have been watched by user.
					for tile in tiles:
						if watched_frames_in_tiles[uID][chunkID].get(tile,None) == None:
							watched_frames_in_tiles[uID][chunkID][tile] = list()
						watched_frames_in_tiles[uID][chunkID][tile].append(FOVNum)

					# for each frame watched in a tile what was the area used.
					for tile in wastage:
						if wasted_area_in_watched_frame[uID][chunkID].get(tile,None)== None:
							wasted_area_in_watched_frame[uID][chunkID][tile] = {}
						wasted_area_in_watched_frame[uID][chunkID][tile][FOVNum] = wastage[tile]

					# the FPS for that second.
					num_frames_in_tile[uID][chunkID]=FOVNum
					FOVNum +=1

	return watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV, wasted_area_in_watched_frame

def getWaste(watched_frames_in_tiles, wasted_area_in_watched_frame, num_frames_in_tile, tileFrameSizes,chunkLength,tileWidth,tileHeight):
	IPerSec = int(round(1000.0/chunkLength)) #number of I-frames in a sec.
	IFrameDist = int(round(25.0/IPerSec)) # Distance between two I-frames
	waste = {}
	area_waste = {}
	drop_frame_waste = {}
	total_bytes = {}
	#print(num_frames_in_tile)
	for uID in watched_frames_in_tiles:
		waste[uID] = {}
		area_waste[uID] = {}
		drop_frame_waste[uID] = {}
		total_bytes[uID] = {}
		baseFrameNum = 0
		for chunkID in watched_frames_in_tiles[uID]:
			waste[uID][chunkID] = 0
			area_waste[uID][chunkID] = 0
			
			
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
						if total_bytes[uID].get(chunkID) is None:
							total_bytes[uID][chunkID] = 0
						total_bytes[uID][chunkID] += tileFrameSizes[tile][baseFrameNum+fId] # size of all frames in tile watched and unwatched.


					if fId not in watched_frames_in_tiles[uID][chunkID][tile]:# if frame id not the watched subset.
						if tileFrameSizes[tile].get(baseFrameNum+fId,None) != None:# if we have the size of it (rare cases where this is maybe false)
							if drop_frame_waste[uID].get(chunkID) is None:
								drop_frame_waste[uID][chunkID] = 0
							drop_frame_waste[uID][chunkID] += tileFrameSizes[tile][baseFrameNum+fId]



			for tile in wasted_area_in_watched_frame[uID][chunkID]:
				for fovNum in wasted_area_in_watched_frame[uID][chunkID][tile]:
					if tileFrameSizes[tile].get(baseFrameNum+fovNum,None) != None:
						if area_waste[uID].get(chunkID) is None:
							area_waste[uID][chunkID] = 0
						tileframeSize = tileFrameSizes[tile][baseFrameNum+fovNum]
						extraArea = wasted_area_in_watched_frame[uID][chunkID][tile][fovNum]
						area_waste[uID][chunkID] += tileframeSize * (extraArea/(tileWidth*tileHeight))

			if area_waste[uID].get(chunkID) is not None and drop_frame_waste[uID].get(chunkID) is not None:
				waste[uID][chunkID] = dropped_frames_in_tiles + wastedAreInTileFrames

	return area_waste, drop_frame_waste,waste,total_bytes

def sum_over_users(total_bytes):

	sum_bytes = {}
	for tile_res_key in total_bytes:
		sum_bytes[tile_res_key] = {}
		for user_id in total_bytes[tile_res_key]:
			for chunk_id in total_bytes[tile_res_key][user_id]:
				if sum_bytes[tile_res_key].get(chunk_id) is None:
					sum_bytes[tile_res_key][chunk_id] = []
				sum_bytes[tile_res_key][chunk_id].append(total_bytes[tile_res_key][user_id][chunk_id]/1e6)

	sum_median_bytes = {}
	for tile_res_key in sum_bytes:
		sum_median_bytes[tile_res_key] = {}
		for chunk_id in sum_bytes[tile_res_key]:
			sum_median_bytes[tile_res_key][chunk_id] = np.percentile(sum_bytes[tile_res_key][chunk_id],50)

	return sum_bytes,sum_median_bytes

def getDisplacements(chunk_length,data):
	numOfFramesInChunk = (chunk_length/1000.) * 25
	dis = {}
	for vID in data:
		for uID in data[vID]:
			dis[uID] = calculateDis(data[vID][uID],chunk_length)

	return dis

def getNumberOfTiles(dis,tileWidth,tileHeight):
	numOfTiles = {}
	for uID in dis:
		numOfTiles[uID] = {}
		for chunkId in dis[uID]:

			#Get coordiantes of displacements.
			yaw = dis[uID][chunkId]['yaw']
			pitch = dis[uID][chunkId]['pitch']
			left = yaw - dis[uID][chunkId]['left']
			right = yaw + dis[uID][chunkId]['right']
			up = pitch + dis[uID][chunkId]['up']
			down = pitch - dis[uID][chunkId]['down']


			#Get coordiantes of displacements.
			w1 = left - (FOV/2.0)
			w2 = right + (FOV/2.0)
			h1 = down - (FOV/2.0)
			h2 = up + (FOV/2.0)

			if w1 < 0:
				w1 = 360 + w1
			if w2 > 360:
				w2 = w2 - 360
			if h1 < 0:
				h1 = 180 + h1
			if h2 > 180:
				h2 = h2 - 180

			if w1 % tileWidth != 0:
				w1 = int(w1/tileWidth)* tileWidth

			if w2 % tileWidth !=0:
				w2 = (int(w2/tileWidth) + 1) * tileWidth

			if h1 % tileHeight != 0:
				h1 = int(h1/tileHeight) * tileHeight

			if h2 % tileHeight != 0:
				h2 = (int(h2/tileHeight) + 1) * tileHeight

			width = w2 - w1
			height = h2 - h1
			if w1 > w2:
				width = (360 - w1) + w2
			if h1 > h2:
				height = (180 - h1) + h2

			if height == 0:
				height = 180
			if width == 0:
				width = 360
			#print("Chunk ID: "+str(chunkId))
			#print("("+str(left)+","+str(right)+")->("+str(down)+","+str(up)+")")
			#print("("+str(w1)+","+str(w2)+")->("+str(h1)+","+str(h2)+")")
			#print("Num of tiles:"+ str((width * height)/(tileWidth*tileHeight)))
			#print "==="

			numOfTiles[uID][chunkId] = (width * height)/(tileWidth*tileHeight)
	#print numOfTiles
	return numOfTiles

	disp_1sec = {} #chunk_length, user_id, chunk_id, direction --> value.
	for chunk_length in displacement:
			count = 1000.0/chunk_length
			disp_1sec[chunk_length] = {}
			for user_id in displacement[chunk_length]:
					disp_1sec[chunk_length][user_id] = {}
					for chunkId in displacement[chunk_length][user_id]:
							chunk_id_1sec = int(math.floor(chunkId/count))
							if disp_1sec[chunk_length][user_id].get(chunk_id_1sec) is None:
									disp_1sec[chunk_length][user_id][chunk_id_1sec] = {}
									disp_1sec[chunk_length][user_id][chunk_id_1sec]['left'] = 0
									disp_1sec[chunk_length][user_id][chunk_id_1sec]['right'] = 0
									disp_1sec[chunk_length][user_id][chunk_id_1sec]['up'] = 0
									disp_1sec[chunk_length][user_id][chunk_id_1sec]['down'] = 0
							for disp in ['left','right','up','down']:
									disp_1sec[chunk_length][user_id][chunk_id_1sec][disp] = max(disp_1sec[chunk_length][user_id][chunk_id_1sec][disp]\
																																					  ,displacement[chunk_length][user_id][chunkId][disp])
	return disp_1sec

def get_raw_data(video_id,user_id):
	files = list()
	data = {}
	for (dirpath, dirnames, filenames) in walk("./traces"):
		for fname in filenames:
				if ".csv" in fname:
					files.append(dirpath+"/"+fname)
	for filename in (files):
		v_id = int(filename.split("vID_")[1].split("_")[0])
		u_id = int(filename.split("uID_")[1].split("_")[0])
		if v_id != video_id or (u_id != user_id and user_id != -1):
			continue
		#print(v_id)
		if data.get(v_id, None) == None:
			data[v_id] = {}
		data[v_id][u_id] = list()
		f = open(filename,'r')
		for line in f.readlines():
			if "yaw" in line:
				continue
			temp = line.split(',')
			playbackTime = float(temp[0])
			x = float(temp[1])
			y = float(temp[2])
			z = float(temp[3])
			data[v_id][u_id].append([playbackTime,x,y,z])
	#print data
	return data

def displacement_over_yaw(displacement):

	A_median_disp = {}
	for chunk_length in displacement:
		A_median_disp[chunk_length] = {}
		for user_id in displacement[chunk_length]:
			A_median_disp[chunk_length][user_id] = {}
			for chunk_id in displacement[chunk_length][user_id]:
				disp = displacement[chunk_length][user_id][chunk_id]['left'] + \
						displacement[chunk_length][user_id][chunk_id]['right']
				A_median_disp[chunk_length][user_id][chunk_id] = disp

	return A_median_disp	



def total_bytes_sum_1sec(total_bytes):
	
	total_bytes_1_sec = {}
	for key in total_bytes:
		chunk_length = int(key.split('_')[1])
		num_of_chunks_to_sum = int(1000/chunk_length)
		total_bytes_1_sec[key] = {}
		for user_id in total_bytes[key]:
			total_bytes_1_sec[key][user_id] = {}
			chunk_id_c = -1
			for chunk_id in total_bytes[key][user_id]:
				if chunk_id % num_of_chunks_to_sum == 0:
					chunk_id_c += 1
				if total_bytes_1_sec[key][user_id].get(chunk_id_c) is None:
					total_bytes_1_sec[key][user_id][chunk_id_c] = 0
				total_bytes_1_sec[key][user_id][chunk_id_c] += total_bytes[key][user_id][chunk_id]
	
	total_bytes_reordered = {}
	for res in total_bytes_1_sec:
		for user_id in total_bytes_1_sec[res]:
			if total_bytes_reordered.get(user_id) is None:
				total_bytes_reordered[user_id] = {}
			for chunk_id in total_bytes_1_sec[res][user_id]:
				if total_bytes_reordered[user_id].get(chunk_id) is None:
					total_bytes_reordered[user_id][chunk_id] = {}
				total_bytes_reordered[user_id][chunk_id][res] = total_bytes_1_sec[res][user_id][chunk_id]

	return total_bytes_reordered

def main():
	'''
		scheme, chunk length, avg frame size
		6X6,	1000,	41069.216			(1.00X)
		12X12,	1000,	43643.12			(1.06X)
		24X18,	1000,	50023.6653333		(1.18X)
		6X6,	200,	83872.566			(2.04X)					
		12X12,	200,	87577.0086667		(2.13X)
		24X18,	200,	98263.8193333		(2.39X)
	'''
	size_threshold = {'6x6_1000':1,'6x6_500':1.15,'6x6_200':1.95,\
					  '12x12_1000':1.10,'12x12_500':1.26,'12x12_200':2.05,\
					  '24x18_1000':1.25,'24x18_500':1.41,'24x18_200':2.37}

	widths = [30]#[60,30,15]
	heights = [15]#[30,15,10]
	chunk_lengths = [1000,500,200]

	displacements_per_scheme = {} #key is scheme, value: list of displacement when this scheme was better.
	for video_id in range(1,31):
		if video_id == 15 or video_id ==16:
			continue		
		print("Video:"+str(video_id))
		data = get_raw_data(video_id,-1)

		displacement_ = {}
		for chunk_length in chunk_lengths:
			#chunk_length, user_id, chunk_id, direction --> value.
			#length 1000. for all chunks, so that we comparing apples to apples.
			displacement_[str(chunk_length)] = getDisplacements(1000.,data) 
		displacement = displacement_over_yaw(displacement_)
		
		area_waste = {} #K1: tile resolution, K2:user id, K3:chunk id --> V: area wasted among watched frames within tiles.
		drop_frame_waste = {}
		waste = {}
		total_bytes = {}
		for tileWidth,tileHeight in zip((widths),(heights)):
			for chunk_length in chunk_lengths:
				key = str(360/tileWidth)+"x"+str(180/tileHeight)+"_"+str(chunk_length)
				tileFrameSizes = get_tile_frame_sizes_threshold((360/tileWidth),(180/tileHeight),chunk_length,size_threshold)
				tileMap = generateMAP(tileWidth,tileHeight)

				watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV,\
					wasted_area_in_watched_frame = getData(data,video_id,chunk_length,\
					tileWidth,tileHeight,tileMap)

				area_waste[key], drop_frame_waste[key], waste[key],total_bytes[key] =\
					getWaste(watched_frames_in_tiles, wasted_area_in_watched_frame, \
					num_frames_in_tile, tileFrameSizes,chunk_length,tileWidth,tileHeight)
		# user_id, chunk_id, scheme_chunkLength -> total_bytes over 1sec.
		total_bytes_reordered_sum_1sec = total_bytes_sum_1sec(total_bytes)

		for user_id in total_bytes_reordered_sum_1sec:
			for chunk_id in total_bytes_reordered_sum_1sec[user_id]:
				val = -1
				resolution = ""
				for key in total_bytes_reordered_sum_1sec[user_id][chunk_id]:
					if val == -1 or val > total_bytes_reordered_sum_1sec[user_id][chunk_id][key]:
						val = total_bytes_reordered_sum_1sec[user_id][chunk_id][key]
						resolution = key 
				chunk_length = str(resolution.split("_")[1])
				if displacement[chunk_length][user_id].get(chunk_id) is None:
					continue
				disp = displacement[chunk_length][user_id][chunk_id]
				if displacements_per_scheme.get(chunk_length) is None:
					displacements_per_scheme[chunk_length] = []
				displacements_per_scheme[chunk_length].append(disp)


	##PERCENTAGE##
	plt.figure(figsize=(6,4))
	plt.subplot(111)
	plt.grid(zorder=0)
	colors = ['g','r','b','magenta']
	styles = ['solid','dashed','densely dotted']
	c = 0
	for chunk_length in chunk_lengths:

		cl = str(chunk_length)
		if displacements_per_scheme.get(cl) is None:
			continue
		print(cl)
		print(len(displacements_per_scheme[cl]))

		sorted_data = np.sort(displacements_per_scheme[cl])
		yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
		plt.plot(sorted_data,yvals,linewidth=3,color=colors[c],linestyle=linestyles[styles[c]],label=chunk_length,zorder = 3)
		c += 1


	plt.yticks(fontweight="bold",size=10)
	plt.ylabel('Frac. of chunks',fontweight="bold",size=10)
	plt.xlabel('Displacement over yaw',fontweight="bold",size=10)
	plt.xticks(fontweight="bold",size=10)
	plt.legend(loc='best',ncol = 3,prop={'size': 10,'weight':'bold'})
	plt.ylim(0,1)

	plt.xlim(0,150)
	kt = key = str(360/widths[0])+"x"+str(180/heights[0])
	plt.title(kt,size=12,fontweight="bold")
	plt.savefig("graphs/displacement_better_chunk_CDF.png",dpi=300,bbox_inches='tight',pad_inches=.05)
	plt.close()


if __name__ == "__main__":
	main()
