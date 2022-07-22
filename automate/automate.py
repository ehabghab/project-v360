#!/usr/bin/python
import sys
import os
import random
import math
import subprocess
from optparse import OptionParser
import time
from datetime import datetime
from os import walk
import time
import shlex
import signal

encoding ="utf8"


def kill_procs():
	os.system("killall -9 server")
	os.system("killall -9 client")
	os.system("killall -9 mm-link")
	os.system("killall -9 mm-delay")
	time.sleep(2)


def handler(signum, frame):
	print("Time out")
	kill_procs()


signal.signal(signal.SIGALRM, handler)
def run_server_and_get_ip(tracefile, videoPath, args):
	
	interfaces_cmd = "ls /sys/class/net/"
	pid1 = subprocess.Popen(shlex.split(interfaces_cmd), stdout=subprocess.PIPE, shell=False)
	interfaces_before_mahimahi, err1 = pid1.communicate()

	#mahimahi_preq_cmd = "sudo sysctl -w net.ipv4.ip_forward=1"
	#pid2 = subprocess.Popen(shlex.split(mahimahi_preq_cmd), stdout=subprocess.PIPE, shell=False)
	#out2, err2 = pid2.communicate()

	#This will create mahimahi with http-server @ port 7717 inside mahimahi shell"
	mahimahi_cmd = "mm-link "+tracefile+" "+tracefile+" ./bin/server " + videoPath + args
	pid3 = subprocess.Popen([mahimahi_cmd],shell=True)

	#wait for a second to update the interfaces (adding mahimahi interface)
	time.sleep(1)
	pid4 = subprocess.Popen(shlex.split(interfaces_cmd), stdout=subprocess.PIPE, shell=False)
	interfaces_after_mahimahi, err4 = pid4.communicate()

	#Figuring out what is the mahimahi interface name.
	interfaces_before_mahimahi=interfaces_before_mahimahi.split()
	interfaces_after_mahimahi=interfaces_after_mahimahi.split()
	mahimahi_interface=""
	for interface in interfaces_after_mahimahi:
		if interface not in interfaces_before_mahimahi:
			mahimahi_interface=interface
			break
	print(mahimahi_interface)
	ip_cmd="/sbin/ifconfig "+mahimahi_interface.decode(encoding)
	pid5 = subprocess.Popen(shlex.split(ip_cmd), stdout=subprocess.PIPE, shell=False)
	ipout, err5 = pid5.communicate()
	ip=""
	for x in ipout.split(b'\n'):
		if b'P-t-P:' in x:
			ip=x.split()[2].split(b'P-t-P:')[1]
	return ip.decode(encoding)



def main():
	
	user_trace_dir = "/home/ehab/Desktop/Project-V360/analysis/traces_system/"
	video_dir = "/home/ehab/Desktop/Videos/"
	bw_trace_dir = "/home/ehab/Desktop/logs_all/mmlink_traces/"        
	tile_size ="sizes.txt"
	quality_name = "psnr_avgs.txt"
	displacement = "/home/ehab/Desktop/Project-V360/analysis/displacement_across_users_p100.txt"
	args_client = {"flare_skip":" -model=Flare -predLR=1 -bufferModel=skip","flare_rebuffer":" -model=Flare -predLR=1 -bufferModel=rebuffer", "utility":" -model=Utility -predLR=1 -bufferModel=skip", "pano_skip":" -model=Pano -predLR=1 -bufferModel=skip", "pano_rebuffer":" -model=Pano -predLR=1 -bufferModel=rebuffer"}
	models = ["pano_skip","pano_rebuffer","flare_skip","utility","flare_rebuffer"]
	args_server = {"flare_skip":" 0", "flare_rebuffer":" 0","utility":" 1","pano_skip":" 0","pano_rebuffer":" 0"}
	videos = ["v1_data","v2_data","v7_data","v8_data","v14_data","v27_data","v28_data"]
	#videos = ["v14_data","v28_data","v12_data","v27_data","v1_data","v2_data"]
	#labels =  ["low","low","low","low","med","med","high","high"]
	labels =  ["low","low","med","med","med","high","high"]
	bw_traces = ["report_car_0001_subtrace5","report_car_0002_subtrace1","report_bus_0001_subtrace1","report_bus_0002_subtrace1","report_bus_0003_subtrace1","report_car_0004_subtrace5","report_train_0002_subtrace3","report_train_0003_subtrace1","report_tram_0001_subtrace2","report_tram_0002_subtrace3","report_tram_0004_subtrace4","report_bicycle_0001_subtrace4","report_bicycle_0002_subtrace2","report_bus_0006_subtrace2","report_foot_0002_subtrace2"]
	#old_bw = ["report_car_0001_subtrace5","report_car_0002_subtrace1","report_bus_0001_subtrace1","report_bus_0002_subtrace1","report_bus_0003_subtrace1"]
	users = {
		"v1_data":[3,9,14,18,24,33,44,51,56,62],
		"v2_data":[2,6,8,12,17,26,37,46,50,57],
		"v6_data":[1,5,12,16,22,27,34,42,51,57],
		"v17_data":[13,16,26,32,38,45,50,55,59,62],
		"v14_data":[6,9,15,24,33,37,45,47,55,60],
		"v28_data":[2,3,14,19,22,26,36,48,50,55],
		"v7_data":[2,7,15,22,28,33,38,41,51,59],
		"v8_data":[4,8,12,16,23,32,36,40,55,62],
		"v12_data":[1,8,14,19,23,30,39,45,52,59],
		"v27_data":[1,7,11,28,31,35,41,42,51,52]
		}

	idx = 0
	os.system("mkdir results")
	for video in videos:
		os.system("mkdir results/"+video)
		label = labels[idx]
		idx+=1
		videoId = int(video.split("_")[0].replace("v",""))
		videoPath = video_dir + video
		videoPsnr = videoPath+"/" + quality_name
		videoSizes = videoPath+"/"  + tile_size
		displacementPath = videoPath+"/"+"displacement_across_users_p100.txt"
		for bw_trace in bw_traces:
			bw_trace_path = bw_trace_dir+bw_trace+"_"+label+".txt"
			for userId in users[video]:
				for model in models:
					user_frame_vp_path = user_trace_dir+ "vid"+str(videoId)+"_uid"+ str(userId)+"_vp_corr_per_frame.txt"
					user_frame_tiles_path = user_trace_dir+ "vid"+str(videoId)+"_uid"+ str(userId)+"_tiles_per_frame_user.txt"

					kill_procs()
					out_dir = "results/"+video+"/"+str(userId)+"_"+model+"_"+str(bw_trace)
					os.system("mkdir "+out_dir)
					server_ip = run_server_and_get_ip(bw_trace_path,videoPath,args_server[model])
					time.sleep(1)

					client_cmd = "./bin/client "+user_frame_tiles_path+" "+user_frame_vp_path+" "+videoSizes+" "+videoPsnr+" "+displacementPath+" "+server_ip+" "
					if "pano" in model:
						client_cmd += " /home/ehab/Desktop/Videos/Pano_tiles_grouping/v"+str(videoId)+"_grouping.txt" +" /home/ehab/Desktop/Videos/videos_bitrates/v"+str(videoId)+"_bitrates.txt "
					client_cmd += args_client[model]
					print(client_cmd)
					pid = subprocess.Popen(client_cmd,shell=True)
					try:	
						signal.alarm(15*60)
						out,err = pid.communicate()
						print(err)
						print(out)
					except :
						print("TIME out")
					os.system("mv client* "+out_dir)
					os.system("mv play* "+out_dir)
					os.system("mv pred* "+out_dir)
					os.system("mv recv* "+out_dir)
					os.system("mv server* "+out_dir)
					os.system("rm -r yuv* ")
					kill_procs()
					time.sleep(5)



if __name__ == "__main__":
	main()


	

		





