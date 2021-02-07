
from pyquaternion import Quaternion
import math
import matplotlib.pyplot as plt
import numpy as np
from os import walk
import os
import matplotlib.patches as mpatches
import    faulthandler
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

def getTileFrameSizes(tileWidth,tileHeight,chunk_length):
	if chunk_length == 200:
		dir = "../split/Width"+str(tileWidth)+"_Height"+str(tileHeight)+"/EXP4"
	elif chunk_length == 1000:
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

def getFrameAndChunkSizes(tileWidth,tileHeight,chunk_length):
	if chunk_length == 200:
		dir = "../split/Width"+str(tileWidth)+"_Height"+str(tileHeight)+"/EXP4"
	elif chunk_length == 1000:
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

	frameSizes = {}
	for tile in tileFrameSizes:
		for frameNum in tileFrameSizes[tile]:
				if frameSizes.get(frameNum,None) == None:
					frameSizes[frameNum] = 0
				frameSizes[frameNum] += tileFrameSizes[tile][frameNum]

	numOfFramesInChunk = (chunk_length/1000.) * 25
	chunkSizes = {}
	for frameNum in frameSizes:
		chunkId = int((frameNum-1)/numOfFramesInChunk)
		if chunkSizes.get(chunkId,None) == None:
			chunkSizes[chunkId] = 0
		chunkSizes[chunkId] += frameSizes[frameNum]



	return frameSizes,chunkSizes

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
			if chunkId not in l:
				displacements[chunkId] = {}
				displacements[chunkId]['yaw'] = yaw
				displacements[chunkId]['pitch'] = pitch
				l.append(chunkId)
				continue


	return displacements

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
    return data

def main():
	for video_id in range(1,31,1):
	    user_id = -1
	    data = get_raw_data(video_id,user_id)
	    Lengths = [1000]#,200]
	    displacement = {}

	    for chunk_length in Lengths:
		    displacement[chunk_length] = getDisplacements(chunk_length,data)



	    disp_yaw = {}
	    disp_pitch = {}
	    for chunk_length in displacement:
			disp_yaw[chunk_length] = {}
			disp_pitch[chunk_length] = {}
			for user_id in displacement[chunk_length]:
				for chunk_id in displacement[chunk_length][user_id]:
					if disp_yaw[chunk_length].get(chunk_id) is None:
						disp_yaw[chunk_length][chunk_id] = list()
						disp_pitch[chunk_length][chunk_id] = list()
					disp_yaw[chunk_length][chunk_id].append(displacement[chunk_length][user_id][chunk_id]['yaw'])
					disp_pitch[chunk_length][chunk_id].append(displacement[chunk_length][user_id][chunk_id]['pitch'])


	    median_x = []
	    median_y = []
	    P90_y = []
	    for chunk_length in disp_yaw:
			for chunk_id in disp_yaw[chunk_length]:
				median_x.append(chunk_id)
				median_y.append(np.percentile(disp_yaw[chunk_length][chunk_id],50))
				P90_y.append(np.percentile(disp_yaw[chunk_length][chunk_id],90))

		#####################################PLOTTING########################################################
	    plt.figure(figsize=(16,6))
	    plt.subplot(111)
	    plt.grid(zorder=0)
	    colors = ['g','r','b','magenta']
	    styles=['o','x','v','^']
	    xticks = list()
	    xlabel = list()

	    plt.scatter(median_x,median_y,linewidth=1,marker=styles[0],color=colors[1],label='median',zorder=3)
	    plt.scatter(median_x,P90_y,linewidth=1,marker=styles[1],color=colors[2],label='p90',zorder=3)
	    for i in range(0,60):
			if i % 2 == 0:
				xlabel.append(i)


	    yticks = []
	    for i in range(0,360,20):
			yticks.append(i)
	    plt.yticks(yticks,fontweight="bold",size=10)
	    plt.ylabel('Yaw at the start of chunk',fontweight="bold",size=12)
	    plt.xlabel('Chunk id',fontweight="bold",size=12)
	    plt.xticks(xlabel,xlabel,fontweight="bold",size=10)
	    #plt.ylim(-2,182)
	    plt.legend(loc='best',prop={'size': 10,'weight':'bold'})

	    plt.title("Video id:"+str(video_id)+", Chunk length:"+str(Lengths[0])+"ms",size=14,fontweight="bold")
	    plt.xlim(-0.5,59.5)
	    plt.savefig("graphs/vID_"+str(video_id)+",CL_"+str(Lengths[0])+"ms_locations_of_users_pitch.png",dpi=300,bbox_inches='tight',pad_inches=.05)
	    plt.close()


if __name__ == "__main__":
    main()
