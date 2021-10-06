
from pyquaternion import Quaternion
import math
import matplotlib.pyplot as plt
import numpy as np
from os import walk
import os

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

def getTypeAndSize():
	frameSizes = {}
	frameTypes = {}

	for line in open("sizes.txt",'r').readlines():
		data = line.split()
		frameSize = int(data[4]) #Bytes
		frameId = int(data[8].split('.')[0])
		frameSizes[frameId] = frameSize

	frameId = 1
	for line in open("framesType.txt",'r').readlines():
		 frameType = line.split("=")[1][0]
		 frameTypes[frameId] = frameType
		 frameId +=1
	return frameSizes,frameTypes

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



def getTileFrameSizes(tileWidth,tileHeight):
	dir = "../../split/Width"+str(tileWidth)+"_Height"+str(tileHeight)+"/EXP4"
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

def main():

    # get filenames of all traces.
    files = list()
    for (dirpath, dirnames, filenames) in walk("./19_1"):
        for fname in filenames:
                if ".csv" in fname:
                    files.append(dirpath+"/"+fname)

	video = 1
	userID = 3
    chunkLength = 200 #chunk length in millisecond
    tileWidth = 360
    tileHeight = 180

    # retrieve traces of interest.
    data = {} #
	#fname vID_%d_uID_%d_MMSYS19_D1.csv
    for fname in files:
        vID = int(fname.split("vID_")[1].split("_")[0])
        uID = int(fname.split("uID_")[1].split("_")[0])
        if vID != video or uID != userID:
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





    #the number of switches.
	#the transmission delay of switch, and decode latency.
    tileWidth = 60
    tileHeight = 30


    numberOfTiles = (360/tileWidth) * (180/tileHeight)
    tileFrameSizes = getTileFrameSizes((360/tileWidth),(180/tileHeight))
    tileChunkSizes = generateTileChunkSizes(tileFrameSizes,chunkLength)
    tileMap = generateMAP(tileWidth,tileHeight)
    #tiles, was = getTiles(tileMap,180,90,tileWidth,tileHeight)
    #print was
    #plotMap(tileMap,180,90,tileWidth,tileHeight)

    IPerSec = int(round(1000.0/chunkLength)) #number of I-frames in a sec.
    IFrameDist = int(round(25.0/IPerSec)) # Distance between two I-frames

    framesWatchedInTile = {} # frames watched within tile. key is (user id --> sec -->tile), value number of frames.
    framesInTile = {} # index of watched frames in chunk, key is (user id --> chunkNum), value list of frames number within tile.
    tilesInFOV = {} # number of tiles in a single FOV
    extraAreaInTileFrame = {}

    for vID in data:
        if vID != video:
            continue
        for uID in data[vID]:
            FOVNum = 1 #number of frames in second (frame counter)
            startTime = -1
            prevFrameTime = 0
            chunkID = -1
            framesWatchedInTile[uID] = {}
            framesInTile[uID] = {}
            tilesInFOV[uID] = {}
            extraAreaInTileFrame[uID] = {}
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
                    if  framesWatchedInTile[uID].get(chunkID,None) == None:
                        framesWatchedInTile[uID][chunkID] = {}
                        extraAreaInTileFrame[uID][chunkID] = {}
                        tilesInFOV[uID][chunkID] = {}

                    tilesInFOV[uID][chunkID][FOVNum] = len(tiles) #to calcuate the total area requested.
					# count how many frames in tile were watched.
                    for tile in tiles:
                        if framesWatchedInTile[uID][chunkID].get(tile,None) == None:
                            framesWatchedInTile[uID][chunkID][tile] = list()

                        framesWatchedInTile[uID][chunkID][tile].append(FOVNum)

					# for each frame watched in a tile what was the area used.
                    for tile in wastage:
						if extraAreaInTileFrame[uID][chunkID].get(tile,None)== None:
							extraAreaInTileFrame[uID][chunkID][tile] = {}
						extraAreaInTileFrame[uID][chunkID][tile][FOVNum] = wastage[tile]

					# the FPS for that second.
                    framesInTile[uID][chunkID]=FOVNum
                    FOVNum +=1


	waste = {}
	ideal = {}
	latency = {} #keys, uid --> chunkid --> start frame number (if not 1 then switch) , value tiles.
	for uID in framesWatchedInTile:
		latency[uID] = {}
		for chunkID in framesWatchedInTile[uID]:
			latency[uID][chunkID] = {}
			for tile in framesWatchedInTile[uID][chunkID]:
				firstFrameInTile = sorted(framesWatchedInTile[uID][chunkID][tile])[0]
				if firstFrameInTile != 1: #there is a switch
					if latency[uID][chunkID].get(firstFrameInTile,None) == None:
						latency[uID][chunkID][firstFrameInTile] = list()
					latency[uID][chunkID][firstFrameInTile].append(tile)


	bandwidth = 9 #mbps
	numOfSwitches = {} #key chunkID, value is number of switches.
	networkDelay = {} #key is chunkID, value is transmission delay caused by switch.
	decodeDelay = {} #key is chunkID --> frames to decode (at beginning) --> number of tiles.

	for uID in latency:
		numOfSwitches[uID] = {}
		networkDelay[uID] = {}
		decodeDelay[uID] = {}
		for chunkID in latency[uID]:
			if len(latency[uID][chunkID]) != 0:
				numOfSwitches[uID][chunkID] = len(latency[uID][chunkID])
				networkDelay[uID][chunkID] = 0
				decodeDelay[uID][chunkID] = {}
				for frameId in latency[uID][chunkID]:
					decodeDelay[uID][chunkID][frameId-1] = len(latency[uID][chunkID][frameId])
					for tile in latency[uID][chunkID][frameId]:
						tileChunkSize = 8. * (tileChunkSizes[chunkID][tile]/1e6) #mbit
						transmissionDelay = tileChunkSize / bandwidth #seconds
						networkDelay[uID][chunkID] += transmissionDelay


	count = 1000.0/chunkLength
	numOfSwitchesSec = {}
	networkDelaySec = {}
	decodeDelaySec = {}

	for uID in networkDelay:
		numOfSwitchesSec[uID] = {}
		networkDelaySec[uID] = {}
		decodeDelaySec[uID] = {}
		for chunkID in networkDelay[uID]:
			chunkSumID = int(math.floor(chunkID/count))

			if numOfSwitchesSec[uID].get(chunkSumID,None) == None:
				numOfSwitchesSec[uID][chunkSumID] = 0
			numOfSwitchesSec[uID][chunkSumID] += numOfSwitches[uID][chunkID]

			if networkDelaySec[uID].get(chunkSumID,None) == None:
				networkDelaySec[uID][chunkSumID] = 0
			networkDelaySec[uID][chunkSumID] += networkDelay[uID][chunkID]

			if decodeDelaySec[uID].get(chunkSumID,None) == None:
				decodeDelaySec[uID][chunkSumID]={}

			for frameId in decodeDelay[uID][chunkID]:
				if decodeDelaySec[uID][chunkSumID].get(frameId,None) == None:
					decodeDelaySec[uID][chunkSumID][frameId] = 0
				decodeDelaySec[uID][chunkSumID][frameId] += decodeDelay[uID][chunkID][frameId]



	#one graph, called decoding latency, avg num of tiles, avg num of frames, and num of switches.
	#number of frames to decode = (num of frames * num of tiles * tile size)/size of original frame.
	# Time series Two y-axises one for netowrk and the other for number of frames to decode.

	decodeList = list()
	networkList = list()
	chunkIdList = list()
	for uID in networkDelaySec:
		for chunkID in networkDelaySec[uID]:
			chunkIdList.append(chunkID+1)
			networkList.append(networkDelaySec[uID][chunkID]*1000.)
			numberOfFramesToDecode = 0
			for frameId in decodeDelaySec[uID][chunkID]: # number of frames to decode
				numberOfFramesToDecode += (frameId * decodeDelaySec[uID][chunkID][frameId]) # (num of frames * num of tiles)

			normalizeFramesToDecode = (numberOfFramesToDecode * tileWidth * tileHeight) / (360. * 180.)
			decodeList.append(normalizeFramesToDecode)


	plt.figure(figsize=(16,6))
	plt.subplot(111)

	plt.scatter(chunkIdList,decodeList,linewidth=2,marker='v',color='b',label = str(360/tileWidth)+"x"+str(180/tileHeight))
	#====================================================================================================
    #the number of switches.
	#the transmission delay of switch, and decode latency.
    tileWidth = 30
    tileHeight = 15


    numberOfTiles = (360/tileWidth) * (180/tileHeight)
    tileFrameSizes = getTileFrameSizes((360/tileWidth),(180/tileHeight))
    tileChunkSizes = generateTileChunkSizes(tileFrameSizes,chunkLength)
    tileMap = generateMAP(tileWidth,tileHeight)
    #tiles, was = getTiles(tileMap,180,90,tileWidth,tileHeight)
    #print was
    #plotMap(tileMap,180,90,tileWidth,tileHeight)

    IPerSec = int(round(1000.0/chunkLength)) #number of I-frames in a sec.
    IFrameDist = int(round(25.0/IPerSec)) # Distance between two I-frames

    framesWatchedInTile = {} # frames watched within tile. key is (user id --> sec -->tile), value number of frames.
    framesInTile = {} # index of watched frames in chunk, key is (user id --> chunkNum), value list of frames number within tile.
    tilesInFOV = {} # number of tiles in a single FOV
    extraAreaInTileFrame = {}

    for vID in data:
        if vID != video:
            continue
        for uID in data[vID]:
            FOVNum = 1 #number of frames in second (frame counter)
            startTime = -1
            prevFrameTime = 0
            chunkID = -1
            framesWatchedInTile[uID] = {}
            framesInTile[uID] = {}
            tilesInFOV[uID] = {}
            extraAreaInTileFrame[uID] = {}
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
                    if  framesWatchedInTile[uID].get(chunkID,None) == None:
                        framesWatchedInTile[uID][chunkID] = {}
                        extraAreaInTileFrame[uID][chunkID] = {}
                        tilesInFOV[uID][chunkID] = {}

                    tilesInFOV[uID][chunkID][FOVNum] = len(tiles) #to calcuate the total area requested.
					# count how many frames in tile were watched.
                    for tile in tiles:
                        if framesWatchedInTile[uID][chunkID].get(tile,None) == None:
                            framesWatchedInTile[uID][chunkID][tile] = list()

                        framesWatchedInTile[uID][chunkID][tile].append(FOVNum)

					# for each frame watched in a tile what was the area used.
                    for tile in wastage:
						if extraAreaInTileFrame[uID][chunkID].get(tile,None)== None:
							extraAreaInTileFrame[uID][chunkID][tile] = {}
						extraAreaInTileFrame[uID][chunkID][tile][FOVNum] = wastage[tile]

					# the FPS for that second.
                    framesInTile[uID][chunkID]=FOVNum
                    FOVNum +=1


	waste = {}
	ideal = {}
	latency = {} #keys, uid --> chunkid --> start frame number (if not 1 then switch) , value tiles.
	for uID in framesWatchedInTile:
		latency[uID] = {}
		for chunkID in framesWatchedInTile[uID]:
			latency[uID][chunkID] = {}
			for tile in framesWatchedInTile[uID][chunkID]:
				firstFrameInTile = sorted(framesWatchedInTile[uID][chunkID][tile])[0]
				if firstFrameInTile != 1: #there is a switch
					if latency[uID][chunkID].get(firstFrameInTile,None) == None:
						latency[uID][chunkID][firstFrameInTile] = list()
					latency[uID][chunkID][firstFrameInTile].append(tile)


	bandwidth = 9 #mbps
	numOfSwitches = {} #key chunkID, value is number of switches.
	networkDelay = {} #key is chunkID, value is transmission delay caused by switch.
	decodeDelay = {} #key is chunkID --> frames to decode (at beginning) --> number of tiles.

	for uID in latency:
		numOfSwitches[uID] = {}
		networkDelay[uID] = {}
		decodeDelay[uID] = {}
		for chunkID in latency[uID]:
			if len(latency[uID][chunkID]) != 0:
				numOfSwitches[uID][chunkID] = len(latency[uID][chunkID])
				networkDelay[uID][chunkID] = 0
				decodeDelay[uID][chunkID] = {}
				for frameId in latency[uID][chunkID]:
					decodeDelay[uID][chunkID][frameId-1] = len(latency[uID][chunkID][frameId])
					for tile in latency[uID][chunkID][frameId]:
						tileChunkSize = 8. * (tileChunkSizes[chunkID][tile]/1e6) #mbit
						transmissionDelay = tileChunkSize / bandwidth #seconds
						networkDelay[uID][chunkID] += transmissionDelay


	count = 1000.0/chunkLength
	numOfSwitchesSec = {}
	networkDelaySec = {}
	decodeDelaySec = {}

	for uID in networkDelay:
		numOfSwitchesSec[uID] = {}
		networkDelaySec[uID] = {}
		decodeDelaySec[uID] = {}
		for chunkID in networkDelay[uID]:
			chunkSumID = int(math.floor(chunkID/count))

			if numOfSwitchesSec[uID].get(chunkSumID,None) == None:
				numOfSwitchesSec[uID][chunkSumID] = 0
			numOfSwitchesSec[uID][chunkSumID] += numOfSwitches[uID][chunkID]

			if networkDelaySec[uID].get(chunkSumID,None) == None:
				networkDelaySec[uID][chunkSumID] = 0
			networkDelaySec[uID][chunkSumID] += networkDelay[uID][chunkID]

			if decodeDelaySec[uID].get(chunkSumID,None) == None:
				decodeDelaySec[uID][chunkSumID]={}

			for frameId in decodeDelay[uID][chunkID]:
				if decodeDelaySec[uID][chunkSumID].get(frameId,None) == None:
					decodeDelaySec[uID][chunkSumID][frameId] = 0
				decodeDelaySec[uID][chunkSumID][frameId] += decodeDelay[uID][chunkID][frameId]



	#one graph, called decoding latency, avg num of tiles, avg num of frames, and num of switches.
	#number of frames to decode = (num of frames * num of tiles * tile size)/size of original frame.
	# Time series Two y-axises one for netowrk and the other for number of frames to decode.

	decodeList = list()
	networkList = list()
	chunkIdList = list()
	for uID in networkDelaySec:
		for chunkID in networkDelaySec[uID]:
			chunkIdList.append(chunkID+1)
			networkList.append(networkDelaySec[uID][chunkID]*1000.)
			numberOfFramesToDecode = 0
			for frameId in decodeDelaySec[uID][chunkID]: # number of frames to decode
				numberOfFramesToDecode += (frameId * decodeDelaySec[uID][chunkID][frameId]) # (num of frames * num of tiles)

			normalizeFramesToDecode = (numberOfFramesToDecode * tileWidth * tileHeight) / (360. * 180.)
			decodeList.append(normalizeFramesToDecode)




	plt.scatter(chunkIdList,decodeList,linewidth=2,marker='x',color='r',label = str(360/tileWidth)+"x"+str(180/tileHeight))

	#====================================================================================================
    #the number of switches.
	#the transmission delay of switch, and decode latency.
    tileWidth = 15
    tileHeight = 10


    numberOfTiles = (360/tileWidth) * (180/tileHeight)
    tileFrameSizes = getTileFrameSizes((360/tileWidth),(180/tileHeight))
    tileChunkSizes = generateTileChunkSizes(tileFrameSizes,chunkLength)
    tileMap = generateMAP(tileWidth,tileHeight)
    #tiles, was = getTiles(tileMap,180,90,tileWidth,tileHeight)
    #print was
    #plotMap(tileMap,180,90,tileWidth,tileHeight)

    IPerSec = int(round(1000.0/chunkLength)) #number of I-frames in a sec.
    IFrameDist = int(round(25.0/IPerSec)) # Distance between two I-frames

    framesWatchedInTile = {} # frames watched within tile. key is (user id --> sec -->tile), value number of frames.
    framesInTile = {} # index of watched frames in chunk, key is (user id --> chunkNum), value list of frames number within tile.
    tilesInFOV = {} # number of tiles in a single FOV
    extraAreaInTileFrame = {}

    for vID in data:
        if vID != video:
            continue
        for uID in data[vID]:
            FOVNum = 1 #number of frames in second (frame counter)
            startTime = -1
            prevFrameTime = 0
            chunkID = -1
            framesWatchedInTile[uID] = {}
            framesInTile[uID] = {}
            tilesInFOV[uID] = {}
            extraAreaInTileFrame[uID] = {}
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
                    if  framesWatchedInTile[uID].get(chunkID,None) == None:
                        framesWatchedInTile[uID][chunkID] = {}
                        extraAreaInTileFrame[uID][chunkID] = {}
                        tilesInFOV[uID][chunkID] = {}

                    tilesInFOV[uID][chunkID][FOVNum] = len(tiles) #to calcuate the total area requested.
					# count how many frames in tile were watched.
                    for tile in tiles:
                        if framesWatchedInTile[uID][chunkID].get(tile,None) == None:
                            framesWatchedInTile[uID][chunkID][tile] = list()

                        framesWatchedInTile[uID][chunkID][tile].append(FOVNum)

					# for each frame watched in a tile what was the area used.
                    for tile in wastage:
						if extraAreaInTileFrame[uID][chunkID].get(tile,None)== None:
							extraAreaInTileFrame[uID][chunkID][tile] = {}
						extraAreaInTileFrame[uID][chunkID][tile][FOVNum] = wastage[tile]

					# the FPS for that second.
                    framesInTile[uID][chunkID]=FOVNum
                    FOVNum +=1


	waste = {}
	ideal = {}
	latency = {} #keys, uid --> chunkid --> start frame number (if not 1 then switch) , value tiles.
	for uID in framesWatchedInTile:
		latency[uID] = {}
		for chunkID in framesWatchedInTile[uID]:
			latency[uID][chunkID] = {}
			for tile in framesWatchedInTile[uID][chunkID]:
				firstFrameInTile = sorted(framesWatchedInTile[uID][chunkID][tile])[0]
				if firstFrameInTile != 1: #there is a switch
					if latency[uID][chunkID].get(firstFrameInTile,None) == None:
						latency[uID][chunkID][firstFrameInTile] = list()
					latency[uID][chunkID][firstFrameInTile].append(tile)


	bandwidth = 9 #mbps
	numOfSwitches = {} #key chunkID, value is number of switches.
	networkDelay = {} #key is chunkID, value is transmission delay caused by switch.
	decodeDelay = {} #key is chunkID --> frames to decode (at beginning) --> number of tiles.

	for uID in latency:
		numOfSwitches[uID] = {}
		networkDelay[uID] = {}
		decodeDelay[uID] = {}
		for chunkID in latency[uID]:
			if len(latency[uID][chunkID]) != 0:
				numOfSwitches[uID][chunkID] = len(latency[uID][chunkID])
				networkDelay[uID][chunkID] = 0
				decodeDelay[uID][chunkID] = {}
				for frameId in latency[uID][chunkID]:
					decodeDelay[uID][chunkID][frameId-1] = len(latency[uID][chunkID][frameId])
					for tile in latency[uID][chunkID][frameId]:
						tileChunkSize = 8. * (tileChunkSizes[chunkID][tile]/1e6) #mbit
						transmissionDelay = tileChunkSize / bandwidth #seconds
						networkDelay[uID][chunkID] += transmissionDelay


	count = 1000.0/chunkLength
	numOfSwitchesSec = {}
	networkDelaySec = {}
	decodeDelaySec = {}

	for uID in networkDelay:
		numOfSwitchesSec[uID] = {}
		networkDelaySec[uID] = {}
		decodeDelaySec[uID] = {}
		for chunkID in networkDelay[uID]:
			chunkSumID = int(math.floor(chunkID/count))

			if numOfSwitchesSec[uID].get(chunkSumID,None) == None:
				numOfSwitchesSec[uID][chunkSumID] = 0
			numOfSwitchesSec[uID][chunkSumID] += numOfSwitches[uID][chunkID]

			if networkDelaySec[uID].get(chunkSumID,None) == None:
				networkDelaySec[uID][chunkSumID] = 0
			networkDelaySec[uID][chunkSumID] += networkDelay[uID][chunkID]

			if decodeDelaySec[uID].get(chunkSumID,None) == None:
				decodeDelaySec[uID][chunkSumID]={}

			for frameId in decodeDelay[uID][chunkID]:
				if decodeDelaySec[uID][chunkSumID].get(frameId,None) == None:
					decodeDelaySec[uID][chunkSumID][frameId] = 0
				decodeDelaySec[uID][chunkSumID][frameId] += decodeDelay[uID][chunkID][frameId]



	#one graph, called decoding latency, avg num of tiles, avg num of frames, and num of switches.
	#number of frames to decode = (num of frames * num of tiles * tile size)/size of original frame.
	# Time series Two y-axises one for netowrk and the other for number of frames to decode.

	decodeList = list()
	networkList = list()
	chunkIdList = list()
	for uID in networkDelaySec:
		for chunkID in networkDelaySec[uID]:
			chunkIdList.append(chunkID+1)
			networkList.append(networkDelaySec[uID][chunkID]*1000.)
			numberOfFramesToDecode = 0
			for frameId in decodeDelaySec[uID][chunkID]: # number of frames to decode
				numberOfFramesToDecode += (frameId * decodeDelaySec[uID][chunkID][frameId]) # (num of frames * num of tiles)

			normalizeFramesToDecode = (numberOfFramesToDecode * tileWidth * tileHeight) / (360. * 180.)
			decodeList.append(normalizeFramesToDecode)




	plt.scatter(chunkIdList,decodeList,linewidth=2,marker='o',color='g',label = str(360/tileWidth)+"x"+str(180/tileHeight))





	xticksL = list()
	for i in range(0,61,2):
		xticksL.append(i)

	plt.yticks(fontweight="bold",size=14)
	plt.ylabel('No. of Frames to Decode',fontweight="bold",size=14)
	plt.legend(loc='best',prop={'size': 14,'weight':'bold'})
	plt.xlabel('Chunk ID',fontweight="bold",size=14)
	plt.xticks(xticksL,fontweight="bold",size=14)

	plt.title("vID:"+str(video)+", uID:"+str(uID)+", "+str(chunkLength) +"ms, "+str(bandwidth)+"mbps")
	plt.xlim(-1,61)
	plt.ylim(0)
	#plt.show()
	plt.savefig("graphs/vID "+str(video)+" uID "+str(uID)+"_chunk length "+str(chunkLength)+"_ms_decode.png",dpi=300)
	#plt.close()









if __name__ == "__main__":
    main()
