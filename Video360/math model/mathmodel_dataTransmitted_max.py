
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


def getFrameAndChunkSizes(tileWidth,tileHeight,chunkLength):
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

	frameSizes = {}
	for tile in tileFrameSizes:
		for frameNum in tileFrameSizes[tile]:
				if frameSizes.get(frameNum,None) == None:
					frameSizes[frameNum] = 0
				frameSizes[frameNum] += tileFrameSizes[tile][frameNum]

	numOfFramesInChunk = (chunkLength/1000.) * 25
	chunkSizes = {}
	for frameNum in frameSizes:
		chunkId = int((frameNum-1)/numOfFramesInChunk)
		if chunkSizes.get(chunkId,None) == None:
			chunkSizes[chunkId] = 0
		chunkSizes[chunkId] += frameSizes[frameNum]



	return frameSizes,chunkSizes

def getCoo(cx,cy):
	offset = FOV/2.0
	x1 = cx - offset
	if (x1 < 0):
		x1 = 360 + x1
	x2 = cx + offset
	if (x2 > 360):
		x2 = x2 - 360
	elif (x2 == 360):
		x2 = 359

	y1 = cy - offset
	if (y1 < 0):
		y1 = 180 - (180 + y1)

	y2 = cy + offset
	if (y2 > 180):
		y2 = 180 - (y2 - 180)

	return x1,x2,y1,y2


def yawMovement(yaw,prevYaw,startYaw,left,right,flip):

	moveRight = yaw - prevYaw #positive if moving to right or neg in case of overlapping.
	moveLeft = prevYaw - yaw  #positive if moving to the left or neg in case of overlapping.
	#if there is an overlapping the comparison to the start is going to be flipped as well.
	if moveRight > 0 and moveRight <= 180: #move to the right no overlapping.
		True#print("move to the right.")
	elif moveRight < 0 and moveRight <= -180: #move to the right overlapping.
		#print("move to the right OVERLAPPED.")
		flip = not flip
	elif moveLeft > 0 and moveLeft <= 180: #move to the left no overlapping
		True#print("move to the left.")
	elif moveLeft < 0 and moveLeft <= -180: #move to the left overlapping.
		#print("move to the left OVERLAPPED.")
		flip = not flip
	elif moveLeft ==0 and moveRight ==0: #still on the x-axis.
		True#print("no movement.")
	else: #Error
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

def calculateDis(rows,chunkLength):
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

		if timestampCal >= chunkId*chunkLength + chunkLength:
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
				#print(str(chunkId)+"-->"+str(yaw))
				continue
			else:
				#print(str(chunkId)+": "+str(yaw)+"-->"+str(yaw))
				left,right,flipHorizantal = yawMovement(yaw,prevYaw,startYaw,left,right,flipHorizantal)
				down,up,flipVertical = pitchMovement(pitch,prevPitch,startPitch,up,down,flipVertical)
				prevYaw = yaw
				prevPitch = pitch
				displacements[chunkId]['left'] = left
				displacements[chunkId]['right'] = right
				displacements[chunkId]['up'] = up
				displacements[chunkId]['down'] = down

	return displacements



def getDisplacements(chunkLength,data):
	numOfFramesInChunk = (chunkLength/1000.) * 25
	dis = {}
	video = 1
	for vID in data:
		if vID != video:
			continue
		for uID in data[vID]:
			dis[uID] = calculateDis(data[vID][uID],chunkLength)

	return dis


def getCenters(dis,tileWidth,tileHeight):
	yaw = dis['yaw']
	pitch = dis['pitch']
	left = yaw - dis['left']
	right = yaw + dis['right']
	up = pitch + dis['up']
	down = pitch - dis['down']

	if left < 0:
		left = 360 + left
	if right >=360:
		right = right - 360
	if up > 180:
		up = up - 180
	if down < 0:
		down = 180 + down



	x1 = int(int(left/tileWidth) * (tileWidth) + (tileWidth/2.0))
	x2 = int(int(right/tileWidth) * (tileWidth) + (tileWidth/2.0))
	y2 = int(int(up/tileHeight) * (tileHeight) + (tileHeight/2.0))
	y1 = int(int(down/tileHeight) * (tileHeight) + (tileHeight/2.0))

	'''print dis
	print str(yaw)+","+str(pitch)+","+str(left)+","+str(right)+","+str(down)+","+str(up)
	print str(x1)+","+str(y1)
	print str(x1)+","+str(y2)
	print str(x2)+","+str(y1)
	print str(x2)+","+str(y2)
	print "======="'''
	return x1,x2,y1,y2

def getMaxDis(dis):

		numOfChunks = 0.0
		displacements = ['left','right','up','down']
		disMax = {}
		for uID in dis:
			for chunkId in dis[uID]:
				numOfChunks += 1.0
				for displacement in displacements:
					if disMax.get(displacement) is None:
						disMax[displacement] = 0
					disMax[displacement]= max(dis[uID][chunkId][displacement],disMax[displacement])


		return disMax

def getNumberOfTilesMax(dis,disMax,tileWidth,tileHeight):
	numOfTiles = {}
	for uID in dis:
		numOfTiles[uID] = {}
		for chunkId in dis[uID]:

			#Get coordiantes of displacements.
			yaw = dis[uID][chunkId]['yaw']
			pitch = dis[uID][chunkId]['pitch']
			centerLeft = yaw - disMax['left']
			centerRight = yaw + disMax['right']
			centerUp = pitch + disMax['up']
			centerDown = pitch - disMax['down']


			#Get coordiantes of displacements.
			lowLeft = centerLeft - (FOV/2.0)
			upperRight = centerRight + (FOV/2.0)
			lowDown = centerDown - (FOV/2.0)
			upperUp = centerUp + (FOV/2.0)
			if lowLeft < 0:
				lowLeft = 360 + lowLeft
			if upperRight > 360:
				upperRight = upperRight - 360
			if lowDown < 0:
				lowDown = 180 + lowDown
			if upperUp > 180:
				upperUp = upperUp - 180

			lowLeftAligned = lowLeft
			if lowLeftAligned % tileWidth != 0:
				lowLeftAligned = int(lowLeftAligned/tileWidth)* tileWidth

			upperRightAligned = upperRight
			if upperRightAligned % tileWidth !=0:
				upperRightAligned = (int(upperRightAligned/tileWidth) + 1) * tileWidth

			lowDownAligned = lowDown
			if lowDownAligned % tileHeight != 0:
				lowDownAligned = int(lowDownAligned/tileHeight) * tileHeight

			upperUpAligned = upperUp
			if upperUpAligned % tileHeight != 0:
				upperUpAligned = (int(upperUpAligned/tileHeight) + 1) * tileHeight



			height = 0
			#height = loweDownAlighned --> centerdown --> centerup --> upperUpAligned
			if lowDownAligned > centerDown:
				height += (180 - lowDownAligned) + centerDown
			else:
				height += centerDown - lowDownAligned

			if centerDown > centerUp:
				height += (180 - centerDown) + centerUp
			else:
				height += centerUp - centerDown

			if centerUp > upperUpAligned:
				height += (180 - centerUp) + upperUpAligned
			else:
				height += upperUpAligned - centerUp


			if height > 180:
				height = 180


			width = 0
			if lowLeftAligned > centerLeft:
				width += (360 - lowLeftAligned) + centerLeft
			else:
				width += centerLeft - lowLeftAligned

			if centerLeft > centerRight:
				width += (360 - centerLeft) + centerRight
			else:
				width += centerRight - centerLeft

			if centerRight > upperRightAligned:
				width += (360 - centerRight) + upperRightAligned
			else:
				width += upperRightAligned - centerRight


			if width > 360:
				width = 360



			#print("Chunk ID: "+str(chunkId))
			#print("Num of tiles:"+ str((width * height)/(tileWidth*tileHeight)))
			#print "==="

			numOfTiles[uID][chunkId] = (width * height)/(tileWidth*tileHeight)
	#print numOfTiles
	return numOfTiles


def main():
    # get filenames of all traces.
    files = list()
    for (dirpath, dirnames, filenames) in walk("./traces"):
        for fname in filenames:
                if ".csv" in fname:
                    files.append(dirpath+"/"+fname)

    video = 1
    userID = 3
    # retrieve traces of interest.
    data = {} #
	#fname vID_%d_uID_%d_MMSYS19_D1.csv
    for fname in (files):
        vID = int(fname.split("vID_")[1].split("_")[0])
        uID = int(fname.split("uID_")[1].split("_")[0])
        if vID != video or userID != uID:
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

    Widths = [60,30,15]
    Heights = [30,15,10]
    Lengths = [1000]
    transmitted = {}
    xAxis = {}
    for tileWidth,tileHeight in zip(Widths,Heights):
		scheme = str(360/tileWidth)+"x"+str(180/tileHeight)
		totalTiles = (360./tileWidth) * (180./tileHeight)
		transmitted[scheme] = {}
		xAxis[scheme] = {}
		for chunkLength in Lengths:
		    print str(tileWidth)+"x"+str(tileHeight)+"-->"+str(chunkLength)
		    transmitted[scheme][chunkLength] = {}
		    xAxis[scheme][chunkLength] = {}
		    frameSizes, chunkSizes = getFrameAndChunkSizes((360/tileWidth),(180/tileHeight),chunkLength)
		    dis = getDisplacements(chunkLength,data)
		    maxDis = getMaxDis(dis)
		    numOfTiles = getNumberOfTilesMax(dis,maxDis,tileWidth,tileHeight)
		    print numOfTiles
		    for uID in numOfTiles:
				transmitted[scheme][chunkLength][uID] = list()
				xAxis[scheme][chunkLength][uID] = list()
				for chunkId in numOfTiles[uID]:
					if chunkSizes.get(chunkId) is None:
						continue
					transmitted[scheme][chunkLength][uID].append((chunkSizes[chunkId] * (numOfTiles[uID][chunkId]/totalTiles))/1e6)
					xAxis[scheme][chunkLength][uID].append(chunkId)

    #print transmitted
	#####################################PLOTTING########################################################
    plt.figure(figsize=(16,6))
    plt.subplot(111)
    plt.grid(axis='y')
    colors = ['g','r','b']
    styles=['o','x','v']
    xticks = list()
    c = 2
    for chunkLength in Lengths:
	    for tileWidth,tileHeight in zip(Widths,Heights):
			scheme = str(360/tileWidth)+"x"+str(180/tileHeight)
			for uID in transmitted[scheme][chunkLength]:
				plt.scatter(xAxis[scheme][chunkLength][uID],transmitted[scheme][chunkLength][uID],linewidth=2,marker=styles[c],color=colors[c],label = scheme)
			c -= 1





    plt.yticks(fontweight="bold",size=14)
    plt.ylabel('Data transmitted(MB)',fontweight="bold",size=14)
    plt.legend(loc='best',ncol=3,prop={'size': 14,'weight':'bold'})
    plt.xlabel('Chunk ID',fontweight="bold",size=14)
    plt.xticks(fontweight="bold",size=14)
    #plt.ylim(0,0.7)

    plt.title("vID:"+str(video)+" User ID:"+str(userID)+" (Math model) max displacement")
    plt.xlim(-1,60)
    plt.savefig("graphs/vID "+str(video)+"_mathmodel_transmittedBytes_max.png",dpi=300)
    #plt.show()


if __name__ == "__main__":
    main()
