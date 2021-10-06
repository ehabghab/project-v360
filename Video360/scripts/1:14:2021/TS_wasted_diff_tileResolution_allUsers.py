
from pyquaternion import Quaternion
import math
import matplotlib.pyplot as plt
import numpy as np
from os import walk
import os
import matplotlib.patches as mpatches

videos = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
FOV = 100
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
def show_values(pc, fmt="%.2f", **kw):
    '''
    Heatmap with text in each cell with matplotlib's pyplot
    Source: http://stackoverflow.com/a/25074150/395857
    By HYRY
    '''
    from itertools import izip
    pc.update_scalarmappable()
    ax = pc.get_axes()
    for p, color, value in izip(pc.get_paths(), pc.get_facecolors(), pc.get_array()):
        x, y = p.vertices[:-2, :].mean(0)
        if np.all(color[:3] > 0.5):
            color = (0.0, 0.0, 0.0)
        else:
            color = (1.0, 1.0, 1.0)
        ax.text(x, y, fmt % value, ha="center", va="center", color=color, **kw)

def cm2inch(*tupl):
    '''
    Specify figure size in centimeter in matplotlib
    Source: http://stackoverflow.com/a/22787457/395857
    By gns-ank
    '''
    inch = 2.54
    if type(tupl[0]) == tuple:
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)

def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels,minn,maxx):
    '''
    Inspired by:
    - http://stackoverflow.com/a/16124677/395857
    - http://stackoverflow.com/a/25074150/395857
    '''

    # Plot it out
    fig, ax = plt.subplots()
    c = ax.pcolor(AUC, edgecolors='k', linestyle= '-', linewidths=0.2, cmap='YlOrRd', vmin=minn, vmax=maxx)

    # put the major ticks at the middle of each cell

    xticks = list()
    yticks = list()

    for i in xticklabels:
        xticks.append(i+.5)

    for i in yticklabels:
        yticks.append(i-.5)

    ax.set_yticks(yticks, minor=False)
    ax.set_xticks(xticks, minor=False)
    ax.set_ylim(0,36)
    ax.set_xlim(0,60)
    # set tick labels
    #ax.set_xticklabels(np.arange(1,AUC.shape[1]+1), minor=False)
    ax.set_xticklabels(xticklabels, minor=False)
    ax.set_yticklabels(yticklabels, minor=False)

    # set title and x/y labels
    plt.title(title)
    plt.xlabel(xlabel,fontsize = 14, fontweight = 'bold')
    plt.ylabel(ylabel,fontsize = 14, fontweight = 'bold')

    # Remove last blank column
    plt.xlim( (0, AUC.shape[1]) )

    # Turn off all the ticks
    ax = plt.gca()
    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False


    # Add color bar
    cbar = plt.colorbar(c,pad = 0.01,aspect=50)#,orientation="horizontal")
    cbar.set_label('Fraction of users', fontsize = 14, fontweight = 'bold', rotation=270)
    cbar.ax.get_yaxis().labelpad = 25

    # Add text in each cell
    #show_values(c)

    # resize
    fig = plt.gcf()
    fig.set_size_inches(cm2inch(40, 20))

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

def generateTileSizes(frameSizes,frameTypes,numberOfTiles,chunkLength):
	tileSizes = {} #key is frame number, value is the size of frame-tile.

	# add I frames based on the chunkLength
	IPerSec = int(round(1000.0/chunkLength)) #number of I-frames in a sec.
	IFrameDist = int(round(25.0/IPerSec)) # Distance between two I-frames

	for i in range(0,60): #number of Second in video
		for j in range(0,IPerSec): #number of I frames in a second
			idx = (i * 25 + j * IFrameDist) + 1
			tileSizes[idx] = frameSizes[(i * 25)+1]
	for frameId in frameSizes:
		if tileSizes.get(frameId,None)==None:
			tileSizes[frameId] = frameSizes[frameId]
	# 51 tiles --> 10% increase
	tileOverhead = ((numberOfTiles-1) / 5) / 100.0
	for frameId in tileSizes:
		frameSize = tileSizes[frameId]
		tileSize = float(frameSize) / numberOfTiles # in case no overhead.
		tileSize = tileSize + (tileSize * tileOverhead)
		tileSizes[frameId] = tileSize
	return tileSizes


def get_tile_frame_sizes_threshold(tile_width,tile_height,chunk_length,size_threshold):
	if chunk_length == 200:
		dir = "../split/Width6_Height6/EXP4"
	elif chunk_length == 1000:
		dir = "../split/Width6_Height6/EXP2"

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
			frame_sizes[frame_num] = 41070# avg 6x6 frame size.     #tile_frame_sizes[tile][frame_num] * 1.

	num_of_tiles = tile_width * tile_height * 1.

	tile_frame_sizes_w_threshold = {}
	for frame_num in frame_sizes:
		tile_frame_size = (frame_sizes[frame_num] / num_of_tiles) \
							* size_threshold[str(tile_width)+"x"+str(tile_height)]
		for i in range(1,int(num_of_tiles)+1):
				if tile_frame_sizes_w_threshold.get(i) is None:
					tile_frame_sizes_w_threshold[i] = {}
				tile_frame_sizes_w_threshold[i][frame_num] = tile_frame_size
	print tile_frame_sizes_w_threshold
	return tile_frame_sizes_w_threshold

def getTileFrameSizes(tileWidth,tileHeight,chunkLength):
	if chunkLength == 200:
		dir = "../split/Width"+str(tileWidth)+"_Height"+str(tileHeight)+"/EXP4"
	elif chunkLength == 1000:
		dir = "../split/Width"+str(tileWidth)+"_Height"+str(tileHeight)+"/EXP2"

	tileFrameSizes = {} #key1 = tile, key2 = frameNum, value size
	count = 1
	for i in range(0,tileHeight): #row
		for j in range(0,tileWidth):
			tileFrameSizes[count] = {} # new tile
			dirTile = dir+"/encoded_payloadExtract/"+str(i+1)+"_c_"+str(j+1)
			fList = os.listdir(dirTile)
			for f in fList:
				frameNum = int(f.split(".")[0])
				tileFrameSize = os.path.getsize(dirTile+"/"+f)
				tileFrameSizes[count][frameNum] = tileFrameSize
			count +=1
	return tileFrameSizes

def generateTileChunkSizes(tileFrameSizes,chunkLength):
    IPerSec = int(round(1000.0/chunkLength)) #number of I-frames in a sec.
    numberOfFramesInChunk = int(round(25.0/IPerSec)) # Distance between two I-frames
    tileChunkSizes = {}
    for tileNum in tileFrameSizes:
		for frameNum in tileFrameSizes[tileNum]:
			chunkID = int(math.ceil((frameNum-1)/numberOfFramesInChunk))
			if tileChunkSizes.get(chunkID,None) ==None:
				tileChunkSizes[chunkID] = {}
			if tileChunkSizes[chunkID].get(tileNum, None) == None:
				tileChunkSizes[chunkID][tileNum] = 0
			tileChunkSizes[chunkID][tileNum] += tileFrameSizes[tileNum][frameNum]
    return tileChunkSizes

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
	for uID in watched_frames_in_tiles:
		waste[uID] = {}
		area_waste[uID] = {}
		drop_frame_waste[uID] = {}
		baseFrameNum = 0
		for chunkID in watched_frames_in_tiles[uID]:
			waste[uID][chunkID] = 0
			area_waste[uID][chunkID] = 0
			drop_frame_waste[uID][chunkID] = 0
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
	return area_waste, drop_frame_waste,waste

def sum_waste_over_users(area_waste, drop_frame_waste, waste):

    area_waste_all_users = {}
    for key in area_waste:
		area_waste_all_users[key] = {}
		for user_id in area_waste[key]:
			for chunk_id in area_waste[key][user_id]:
				if area_waste_all_users[key].get(chunk_id) is None:
					area_waste_all_users[key][chunk_id] = []
				area_waste_all_users[key][chunk_id].append(area_waste[key][user_id][chunk_id]* 1./1e6)

    drop_frame_waste_all_users = {}
    for key in drop_frame_waste:
		drop_frame_waste_all_users[key] = {}
		for user_id in drop_frame_waste[key]:
			for chunk_id in drop_frame_waste[key][user_id]:
				if drop_frame_waste_all_users[key].get(chunk_id) is None:
					drop_frame_waste_all_users[key][chunk_id] = []
				drop_frame_waste_all_users[key][chunk_id].append(drop_frame_waste[key][user_id][chunk_id] * 1./1e6)


    waste_all_users = {}
    for key in waste:
		waste_all_users[key] = {}
		for user_id in waste[key]:
			for chunk_id in waste[key][user_id]:
				if waste_all_users[key].get(chunk_id) is None:
					waste_all_users[key][chunk_id] = []
				waste_all_users[key][chunk_id].append(waste[key][user_id][chunk_id] * 1./1e6)

    return area_waste_all_users,drop_frame_waste_all_users,waste_all_users

def main():

    # get filenames of all traces.
    files = list()
    for (dirpath, dirnames, filenames) in walk("./traces"):
        for fname in filenames:
                if ".csv" in fname:
                    files.append(dirpath+"/"+fname)

	size_threshold = {'6x6':1,'12x12':1.07,'24x18':1.22}
    for i in range(1,2):
	    video = i
	    # retrieve traces of interest.
	    data = {}
	    for fname in files:
	        vID = int(fname.split("vID_")[1].split("_")[0])
	        uID = int(fname.split("uID_")[1].split("_")[0])
	        if vID != video:
	            continue
	        if data.get(vID, None) == None:
	            data[vID] = {}
	        data[vID][uID] = list()
	        f = open(fname,'r')
	        for line in f.readlines():
	            if "yaw" in line:
	                continue
	            temp = line.split(',')
	            playbackTime = float(temp[0])
	            x = float(temp[1])
	            y = float(temp[2])
	            z = float(temp[3])
	            data[vID][uID].append([playbackTime,x,y,z])






	    chunkIdAll = {}
	    networkDelayAll = {} # tileResultion->bandwidth->uID, network delay for switched tiles throught the sessions (chunkID->networkDelay[chunkID])
	    chunkLength = 1000 #chunk length in millisecond
	    widths = [60,30,15]
	    heights = [30,15,10]
	    area_waste = {} #K1: tile resolution, K2:user id, K3:chunk id --> V: area wasted among watched frames within tiles.
	    drop_frame_waste = {}
	    waste = {}
	    for tileWidth,tileHeight in zip((widths),(heights)):
			print (str(tileWidth)+","+str(tileHeight))
			key = str(tileWidth)+"x"+str(tileHeight)
			numberOfTiles = (360/tileWidth) * (180/tileHeight)
			tileFrameSizes = get_tile_frame_sizes_threshold((360/tileWidth),(180/tileHeight),chunkLength,size_threshold)
			tileMap = generateMAP(tileWidth,tileHeight)
			watched_frames_in_tiles, num_frames_in_tile, num_tiles_in_FOV, wasted_area_in_watched_frame = getData(data,video,chunkLength,tileWidth,tileHeight,tileMap)
			area_waste[key], drop_frame_waste[key], waste[key] = getWaste(watched_frames_in_tiles, wasted_area_in_watched_frame, num_frames_in_tile, tileFrameSizes,chunkLength,tileWidth,tileHeight)



	    area_waste_all_users,drop_frame_waste_all_users,waste_all_users = sum_waste_over_users(area_waste, drop_frame_waste, waste)
	    #print sorted(waste['15x10'])
	    min10 = {}
	    max90 = {}

	    min10['area_waste_all_users'] = -1
	    max90['area_waste_all_users'] = -1
	    min10['drop_frame_waste_all_users'] = -1
	    max90['drop_frame_waste_all_users'] = -1
	    min10['waste_all_users'] = -1
	    max90['waste_all_users'] = -1

	    for key in area_waste_all_users:
			for chunk_id in area_waste_all_users[key]:
				per10 = np.percentile(area_waste_all_users[key][chunk_id],10)
				per90 = np.percentile(area_waste_all_users[key][chunk_id],90)
				if min10['area_waste_all_users'] == -1 or min10['area_waste_all_users'] > per10:
					min10['area_waste_all_users'] = per10
				if max90['area_waste_all_users'] == -1 or max90['area_waste_all_users'] < per90:
					max90['area_waste_all_users'] = per90

	    for key in drop_frame_waste_all_users:
			for chunk_id in drop_frame_waste_all_users[key]:
				per10 = np.percentile(drop_frame_waste_all_users[key][chunk_id],10)
				per90 = np.percentile(drop_frame_waste_all_users[key][chunk_id],90)
				if min10['drop_frame_waste_all_users'] == -1 or min10['drop_frame_waste_all_users'] > per10:
					min10['drop_frame_waste_all_users'] = per10
				if max90['drop_frame_waste_all_users'] == -1 or max90['drop_frame_waste_all_users'] < per90:
					max90['drop_frame_waste_all_users'] = per90

	    for key in waste_all_users:
			for chunk_id in waste_all_users[key]:
				per10 = np.percentile(waste_all_users[key][chunk_id],10)
				per90 = np.percentile(waste_all_users[key][chunk_id],90)
				if min10['waste_all_users'] == -1 or min10['waste_all_users'] > per10:
					min10['waste_all_users'] = per10
				if max90['waste_all_users'] == -1 or max90['waste_all_users'] < per90:
					max90['waste_all_users'] = per90


	    for key in waste_all_users:
		    plt.figure(figsize=(16,6))
		    plt.subplot(111)
		    colors = ['b','r','g']
		    styles=['','xxx','//']
		    xticks = list()
		    for chunk_id in waste_all_users[key]:
				box_pos = chunk_id+1
				if box_pos % 2 == 0:
					xticks.append(box_pos)
				if chunk_id >=60:
					continue
				boxprops = dict(linewidth=2, color=colors[0],facecolor='white')
				boxplot = plt.boxplot(waste_all_users[key][chunk_id],showfliers=False,positions=[box_pos-.1]\
									  ,widths=[.2],whis=[10,90], boxprops=boxprops,patch_artist=True)
				modifybox(boxplot,waste_all_users[key][chunk_id],[10,90],2,'k','k',styles[0])
		    plt.yticks(fontweight="bold",size=14)
		    plt.ylabel('Data waste (MB)',fontweight="bold",size=14)
		    #plt.legend(loc='best',prop={'size': 14,'weight':'bold'})
		    plt.xlabel('Chunk id',fontweight="bold",size=14)
		    plt.xticks(xticks,xticks,fontweight="bold",size=14)

		    plt.title("vID:"+str(video))
		    plt.xlim(0,61)

		    thres = (max90['waste_all_users'] - min10['waste_all_users']) * .1
		    s_text = str(360/int(key.split('x')[0])) + "X"+ str(180/int(key.split('x')[1]))
		    plt.text(58.5, max90['waste_all_users']+(thres/2.), s_text,fontsize=10,fontweight="bold",bbox=dict(fc="none",color='r'))

		    plt.ylim(min10['waste_all_users']-thres,max90['waste_all_users']+thres)
		    #plt.show()
		    plt.savefig("graphs/vID "+str(video)+"_boxplot_data_waste_"+key+".png",dpi=300,bbox_inches='tight', pad_inches=0)
			#plt.close()















if __name__ == "__main__":
    main()
