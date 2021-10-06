
from pyquaternion import Quaternion
import math
import matplotlib.pyplot as plt
import numpy as np
from os import walk
import os

videos = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
tileWidth = 60
tileHeight = 30
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
    cbar.set_label('Fraction of watched frames', fontsize = 14, fontweight = 'bold', rotation=270)
    cbar.ax.get_yaxis().labelpad = 25

    # Add text in each cell
    #show_values(c)

    # resize
    fig = plt.gcf()
    fig.set_size_inches(cm2inch(40, 20))

def plotMap(tileMap,cx,cy):
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


def getTiles(map,cx,cy):
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
    tiles = list()

    if not upflipped and not downflipped:
        if xdl < xdr: #It is not wrapping around
            for j in range(int(yu),int(yd),-tileHeight):
                for i in range(int(xul),int(xur),tileWidth):
                    tiles.append(map[i][j])
        else:
            for j in range(int(yu),int(yd),-tileHeight):
                for i in range(int(xul), 360, tileWidth):
                    tiles.append(map[i][j])
                for i in range(0, int(xur), tileWidth):
                    tiles.append(map[i][j])

    elif upflipped:
        #Tiles from lower coordinates to center
        #no overlapping on lower coordinates
        if xdl < xdr:
            for j in range(int(yd)+tileHeight,181,tileHeight):
                for i in range(int(xdl),int(xdr),tileWidth):
                    tiles.append(map[i][j])
        #overlapping lower coordinates
        elif xdl > xdr:
            for j in range(int(yd)+tileHeight,181,tileHeight):
                for i in range(int(xdl),360,tileWidth):
                    tiles.append(map[i][j])
                for i in range(0,int(xdr),tileWidth):
                    tiles.append(map[i][j])

        #Tiles from upper coordinates from/to center
        #no overlapping on upper coordinates
        if xul < xur:
            for j in range(int(yu)+tileHeight,181,tileHeight):
                for i in range(int(xul),int(xur),tileWidth):
                    tiles.append(map[i][j])
        # overlapping upper coordinates
        elif xul > xur:
            for j in range(int(yu)+tileHeight,181,tileHeight):
                for i in range(int(xul),360,tileWidth):
                    tiles.append(map[i][j])
                for i in range(0,int(xur),tileWidth):
                    tiles.append(map[i][j])

        if xul > xur and xdl > xdr:
            print ("Error: overlapping upper and lower coordinates")

    elif downflipped:
        if xul < xur:
            for j in range(int(yu),0,-tileHeight):
                for i in range(int(xul),int(xur),tileWidth):
                    tiles.append(map[i][j])
        elif xul > xur:
            for j in range(int(yu),0,-tileHeight):
                for i in range(int(xul),360,tileWidth):
                    tiles.append(map[i][j])
                for i in range(0,int(xur),tileWidth):
                    tiles.append(map[i][j])

        if xdl < xdr:
            for j in range(int(yd),0,-tileHeight):
                for i in range(int(xdl),int(xdr),tileWidth):
                    tiles.append(map[i][j])
        elif xdl > xdr:
            for j in range(int(yd),0,-tileHeight):
                for i in range(int(xdl),360,tileWidth):
                    tiles.append(map[i][j])
                for i in range(0,int(xdr),tileWidth):
                    tiles.append(map[i][j])


        if xul > xur and xdl > xdr:
            print ("Error: overlapping upper and lower coordinates")



    '''wastage = {} #key is tile number, value is the fraction wasted.
    if y1s < y2s:
        for j in range(y2s, y1s, -tileHeight):
            sw1 = x1s + tileWidth - x1
            sw2 = x2-(x2s - tileWidth)
            if j == y2s:
                sl = y2 - (y2s - tileHeight)
            elif j == y1s+tileHeight:
                sl = j - y1
            else:
                sl = tileHeight
            waste1 = ((tileWidth * tileHeight) - (sw1*sl))
            wastage [map[x1s][j]] = float("%.2f"%waste1)
            waste2 = ((tileWidth * tileHeight) - (sw2*sl))
            wastage [map[x2s-tileWidth][j]] = float("%.2f"%waste2)


    else:
        for j in range(y2s, 0, -tileHeight):
            sw1 = x1s + tileWidth - x1
            sw2 = x2-(x2s - tileWidth)
            if j == y2s:
                sl = y2 - (y2s - tileHeight)
            else:
                sl = tileHeight
            waste1 = ((tileWidth * tileHeight) - (sw1*sl))
            wastage [map[x1s][j]] = float("%.2f"%waste1)
            waste2 = ((tileWidth * tileHeight) - (sw2*sl))
            wastage [map[x2s-tileWidth][j]] = float("%.2f"%waste2)

        for j in range(180, y1s, -tileHeight):
            sw1 = x1s + tileWidth - x1
            sw2 = x2-(x2s - tileWidth)
            if j == y1s+tileHeight:
                sl = j - y1
            else:
                sl = tileHeight
            waste1 = ((tileWidth * tileHeight) - (sw1*sl))
            wastage [map[x1s][j]] = float("%.2f"%waste1)
            waste2 = ((tileWidth * tileHeight) - (sw2*sl))
            wastage [map[x2s-tileWidth][j]] = float("%.2f"%waste2)



    if x1s < x2s:
        for i in range(x1s+tileWidth, x2s-tileWidth, tileWidth):
            sl1 = y2 - (y2s-tileHeight)
            sl2 = (y1s + tileHeight) - y1
            sw = tileWidth
            waste1 = ((tileWidth * tileHeight) - (sw*sl2))
            wastage[map[i][y1s+tileHeight]] = float("%.2f"%waste1)
            waste2 = ((tileWidth * tileHeight) - (sw*sl1))
            wastage[map[i][y2s]] = float("%.2f"%waste2)
    else:
        for i in range(x1s+tileWidth, 360, tileWidth):
            sl1 = y2 - (y2s-tileHeight)
            sl2 = (y1s + tileHeight) - y1
            sw = tileWidth
            waste1 = ((tileWidth * tileHeight) - (sw*sl2))
            wastage[map[i][y1s+tileHeight]] = float("%.2f"%waste1)
            waste2 = ((tileWidth * tileHeight) - (sw*sl1))
            wastage[map[i][y2s]] = float("%.2f"%waste2)

        for i in range(0, x2s-tileWidth, tileWidth):
            sl1 = y2 - (y2s-tileHeight)
            sl2 = (y1s + tileHeight) - y1
            sw = tileWidth
            waste1 = ((tileWidth * tileHeight) - (sw*sl2))
            wastage[map[i][y1s+tileHeight]] = float("%.2f"%waste1)
            waste2 = ((tileWidth * tileHeight) - (sw*sl1))
            wastage[map[i][y2s]] = float("%.2f"%waste2)'''






    return tiles,None#tiles,wastage



def generateMAP():
    map = {}
    blockNum = 1
    for y in range (180,0,-tileHeight):
        for x in range(0,360,tileWidth):
            if map.get(x,None) == None:
                map[x] = {}
            map[x][y]=blockNum
            blockNum += 1
    return map

def main():

    # get filenames of all traces.
    files = list()
    for (dirpath, dirnames, filenames) in walk("./19_1"):
        for fname in filenames:
                if ".csv" in fname:
                    files.append(dirpath+"/"+fname)

    # retrieve traces of interest.
    data = {} #
    for fname in files:
        vID = int(fname.split("vID_")[1].split("_")[0])
        uID = int(fname.split("uID_")[1].split("_")[0])
        if vID not in videos:
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

    # get chunk sizes of videos of interest.
    chunkSize = {}
    for vID in videos:
        chunkSize[vID] = {}
        files = list()
        for (dirpath, dirnames, filenames) in walk("videos/vID_"+str(vID)):
            for fname in filenames:
                if ".m4s" in fname  :
                    files.append(dirpath+"/"+fname)
        for f in files:
            file_stats = os.stat(f)
            cID = int(f.split('/')[2].split('.')[0].split('_')[1])
            chunkSize[vID][cID] = file_stats.st_size


    tileMap = generateMAP()
    #tiles, was = getTiles(tileMap,180,90)
    #tiles, was = getTiles(tileMap,180,90)
    #print tiles
    #plotMap(tileMap,180,90)
    video = 6
    framesW = {} # frames watched within tile. key is (user id --> sec -->tile), value number of frames.
    framesS = {} # number of frames within the sec, key is (user id --> sec), value number of frames within tile.
    for vID in data:
        if vID != video:
            continue
        for uID in data[vID]:
            t = -1
            sec = -1
            f = 1 #number of frames in second (frame counter)
            framesW[uID] = {}
            framesS[uID] = {}
            for row in data[vID][uID]:
                timestamp = row[0]      #sec.msec
                yaw = math.degrees(row[1]) + 180
                pitch = math.degrees(row[2]) + 90
                roll = math.degrees(row[3])

                # if we moved to next sec in video
                if int(timestamp) != sec:
                    sec = int(timestamp)
                    f = 1
                #frames are 30msec apart.
                if (timestamp - t)*1000 >=30 or t == -1:
                    if  framesW[uID].get(sec,None) == None:
                        framesW[uID][sec] = {}
                    t = timestamp
                    tiles,wastage = getTiles(tileMap,yaw,pitch)
                    for tile in tiles:
                        if framesW[uID][sec].get(tile,None) == None:
                            framesW[uID][sec][tile] = 0
                        framesW[uID][sec][tile] = framesW[uID][sec][tile] + 1
                    framesS[uID][sec]=f
                    f +=1




	#y-axis is the tile number
	#x-axis is time.
	#fraction of users


	#tile (fraction of users, avg watch time)

	tnumU = {} 	#key tile number--> sec, value number of users
	tTimeL = {} #key is tile number--> sec, avg watch time.
	frames = {} #key is sec, value is frames
	for uID in framesW:
		for sec in framesW[uID]:
			if frames.get(sec, None) == None:
				frames[sec] = 0
			frames[sec] = frames[sec]+framesS[uID][sec]
			for tile in framesW[uID][sec]:
				if tnumU.get(tile,None) == None:
					tnumU[tile] = {}
				if tnumU[tile].get(sec,None) == None:
					tnumU[tile][sec] = 0
				tnumU[tile][sec] +=1

				if tTimeL.get(tile,None) == None:
					tTimeL[tile] = {}
				if tTimeL[tile].get(sec, None) == None:
					tTimeL[tile][sec] = list()
				tTimeL[tile][sec].append(framesW[uID][sec][tile])


	for uID in framesW:
		for sec in framesW[uID]:
			for tile in framesW[uID][sec]:
				if tile ==28 and sec == 26:
					print "("+str(framesW[uID][sec][tile])+","+str(framesS[uID][sec])+")"


	data = np.ndarray(shape=(37,61))
	frames[sec]
	minn = -1
	maxx = -1
	for tile in tTimeL:
		for sec in tTimeL[tile]:
			if tile == 28 and sec == 26:
				print sum(tTimeL[tile][sec])
				print frames[sec]
			data[tile][sec] = sum(tTimeL[tile][sec])*1./ frames[sec]
			minn = data[tile][sec] if data[tile][sec] < minn or minn == -1 else minn
			maxx = data[tile][sec] if data[tile][sec] > maxx or maxx == -1 else maxx

	#print tnumU[22]

    x_axis_size = data.shape[1]
    y_axis_size = data.shape[0]
    #title = "Title"
    xlabel= "Time (sec)"
    ylabel= "Tile number"
    xticklabels = range(0, x_axis_size+1,2) # could be text
    yticklabels = range(2, y_axis_size+1,2) # could be text

    heatmap(data, '', xlabel, ylabel, xticklabels, yticklabels,minn,maxx)
    plt.savefig('heatmap_fractionOfWatchedFrames_tile_sec_VID'+str(video)+'.png', dpi=300, format='png', bbox_inches='tight') # use format='svg' or 'pdf' for vectorial pictures
    plt.show()











    #how often user change, how many tiles.


if __name__ == "__main__":
    main()
