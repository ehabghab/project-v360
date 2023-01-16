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
	bw_trace_dir ="/home/ehab/Desktop/mmlink_traces_raw_to_use/"## "/home/ehab/Desktop/mmlink_traces_raw_to_use/"#    
	tile_size ="sizes.txt"
	quality_name = "psnr_avgs.txt"

	args_client = { "journal":" -model=Journal -predLR=1 -bufferModel=journalRebuffer JournalCoraseABR=true",
					"Flare_with_background_stream": "-model=Journal -predLR=1 -bufferModel=journalRebuffer JournalCoraseABR=false "

					"flare_skip_1sec":" -model=Flare -predLR=1 -bufferModel=skip -predictionWindow=1 ",
					"flare_skip_3sec":" -model=Flare -predLR=1 -bufferModel=skip -predictionWindow=3 ",
					
					"flare_rebuffer_1sec":" -model=Flare -predLR=1 -bufferModel=rebuffer -predictionWindow=1 ", 
					"flare_rebuffer_3sec":" -model=Flare -predLR=1 -bufferModel=rebuffer -predictionWindow=3 ", 
					
					"pano_skip_1sec":" -model=Pano -predLR=1 -bufferModel=skip -predictionWindow=1 ", 
					"pano_skip_3sec":" -model=Pano -predLR=1 -bufferModel=skip -predictionWindow=3 ", 
					
					"pano_rebuffer_1sec":" -model=Pano -predLR=1 -bufferModel=rebuffer -predictionWindow=1 ",
					"pano_rebuffer_3sec":" -model=Pano -predLR=1 -bufferModel=rebuffer -predictionWindow=3 ",

					"utility":" -model=Utility -predLR=1 -bufferModel=skip -UtilityCoraseBackgroundStream=false ", 
					"utility_360_background":" -model=Utility -predLR=1 -bufferModel=UtilityJskip -UtilityCoraseBackgroundStream=true ", 

					}

	args_server = { "journal":" 0 ",
					"Flare_with_background_stream": " 0 ",

					"flare_skip_1sec":" 0 ",
					"flare_skip_3sec":" 0 ",
					
					"flare_rebuffer_1sec":" 0 ",
					"flare_rebuffer_3sec":" 0 ",
					
					"pano_skip_1sec":" 0 ",
					"pano_skip_3sec":" 0 ",
					
					"pano_rebuffer_1sec":" 0 ",
					"pano_rebuffer_3sec":" 0 ",

					"utility":" 1 ",
					"utility_360_background":" 1 ",

					}

	models = ["pano_rebuffer_3sec","flare_rebuffer_1sec","flare_rebuffer_3sec"]

	videos = ["v1_data","v2_data","v7_data","v8_data","v14_data","v27_data","v28_data"] #"v1_data","v2_data","v7_data","v8_data","v14_data","v27_data",
	bw_traces_raw_exp1_exp2 = ["report_bus_0003_subtrace1","report_car_0004_subtrace2","report_foot_0004_subtrace1","report_train_0003_subtrace1"]#,"report_bus_0003_subtrace2","report_foot_0006_subtrace1","report_foot_0004_subtrace2","report_car_0002_subtrace1","report_foot_0002_subtrace1","report_car_0004_subtrace1","report_car_0004_subtrace3"]
	bw_traces_raw_exp3 = ["10_B_2020.02.13_13.57.29_subtrace44","4_B_2020.02.13_13.57.29_subtrace2","8_B_2020.02.13_13.57.29_subtrace26","1_B_2019.12.16_13.40.04_subtrace14","5_B_2020.02.13_13.57.29_subtrace10","9_B_2020.02.13_13.57.29_subtrace33","2_B_2020.01.16_10.43.34_subtrace2","6_B_2020.02.13_13.57.29_subtrace11","3_B_2020.01.16_10.43.34_subtrace7","7_B_2020.02.13_13.57.29_subtrace18"]#"10_B_2020.02.13_13.57.29_subtrace44","4_B_2020.02.13_13.57.29_subtrace2"
	users = {
		"v1_data":[3,9,14,18],#24,33,44,51,56,62],
		"v2_data":[2,6,8,12],#17,26,37,46,50,57],
		"v7_data":[2,7,15,22],#28,33,38,41,51,59],
		"v8_data":[4,8,12,16],#23,32,36,40,55,62],
		"v14_data":[6,9,15,24],#33,37,45,47,55,60],
		"v27_data":[1,7,11,28],#31,35,41,42,51,52],
		"v28_data":[2,3,14,19],#22,26,36,48,50,55],
		}

	idx = 0
	os.system("mkdir results")
	for video in videos:
		os.system("mkdir results/"+video)
		idx+=1
		videoId = int(video.split("_")[0].replace("v",""))
		videoPath = video_dir + video
		videoPsnr = videoPath+"/" + quality_name
		vidoePsnrChunk = videoPath+"/psnr_chunk.txt"
		videoSPSNR = video_dir+"/pano-static-pspnr/static_pspnr_"+"%03d"%(videoId)+".txt"
		videoSizes = videoPath+"/"  + tile_size
		displacementPath = videoPath+"/"+"displacement_across_users_p100.txt"
		displacementTrainingPath = video_dir+"various_displacements/v"+str(videoId)+"_displacement_across_users_p100_all.txt"
		baseLayerSize = videoPath+"/QP00/sizes_b.txt "
		for bw_trace in bw_traces_raw_exp1_exp2:
			bw_trace_path = bw_trace_dir+bw_trace+".txt"
			for userId in users[video]:
				for model in models:
					user_frame_vp_path = user_trace_dir+ "vid"+str(videoId)+"_uid"+ str(userId)+"_vp_corr_per_frame.txt"
					user_frame_tiles_path = user_trace_dir+ "vid"+str(videoId)+"_uid"+ str(userId)+"_tiles_per_frame_user.txt"

					kill_procs()
					out_dir = "results/"+video+"/"+str(userId)+"_"+model+"_"+str(bw_trace)
					os.system("mkdir "+out_dir)
					server_ip = run_server_and_get_ip(bw_trace_path,videoPath,args_server[model])
					time.sleep(1)

					client_cmd = "./bin/client "+user_frame_tiles_path+" "+user_frame_vp_path+" "+videoSizes+" "+videoPsnr+" "+displacementTrainingPath+" "+server_ip+" "
					#client_cmd = "./bin/client "+user_frame_tiles_path+" "+user_frame_vp_path+" "+videoSizes+" "+videoSPSNR+" "+displacementTrainingPath+" "+server_ip+" "
					
					if "pano" in model:
						#client_cmd += " /home/ehab/Desktop/Videos/fine_grain_groups.txt" +" /home/ehab/Desktop/Videos/videos_bitrates/v"+str(videoId)+"_bitrates.txt "
						client_cmd += " /home/ehab/Desktop/Videos/Pano_tiles_grouping/v"+str(videoId)+"_grouping.txt" +" /home/ehab/Desktop/Videos/videos_bitrates/v"+str(videoId)+"_bitrates.txt "
						#client_cmd += " /home/ehab/Desktop/Videos/pano-static-pspnr/v"+str(videoId)+"_grouping_spspnr.txt" +" /home/ehab/Desktop/Videos/videos_bitrates/v"+str(videoId)+"_bitrates.txt "
					if "journal" in model:
						client_cmd += baseLayerSize
					
					if "utility_360_background" in model:
						client_cmd += baseLayerSize +" "+vidoePsnrChunk

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



def main_study():
	
	video_dir = "/home/ehab/Desktop/Videos/"
	bw_trace_dir = "/home/ehab/Desktop/mmlink_traces_raw_to_use/"#"/home/ehab/Desktop/logs_all/mmlink_traces_raw_to_use/"        
	tile_size ="sizes.txt"
	quality_name = "psnr_avgs.txt"
	displacement = "/home/ehab/Desktop/Project-V360/analysis/displacement_across_users_p100.txt"
	args_client = {"Flare":" -model=Flare -predLR=1 -bufferModel=live", "Dragonfly":" -model=Utility -predLR=1 -bufferModel=skip", "Pano":" -model=Pano -predLR=1 -bufferModel=live"}
	args_server = {"Flare":" 0", "Dragonfly":" 1","Pano":" 0"}
	models ={"Pano":"pano"}
	main_dir = "/home/ehab/Desktop/aug_15_ehab_study"
	files = os.listdir(main_dir)
	users_corr_files = []
	for f_corr in files:	
		if "corr" in f_corr:
			users_corr_files.append(f_corr)

	os.system("mkdir results_study")
	for f_corr in users_corr_files:
		data = f_corr.split("_")
		user_id = data[0].replace("u","")
		video_id = int(data[1].replace("v",""))
		model = data[2]
		trace_id = f_corr.split("trace_")[1].split("_corr")[0]
		videoPath = video_dir +"v" +str(video_id)+"_data"
		videoPsnr = videoPath+"/" + quality_name
		videoSizes = videoPath+"/"  + tile_size
		displacementPath = videoPath+"/"+"displacement_across_users_p100.txt"
		for bw_trace in [trace_id]:
			bw_trace_path = bw_trace_dir+bw_trace+".txt"
			for model in [model]:
				user_frame_vp_path = main_dir+"/"+f_corr
				user_frame_tiles_path = main_dir+"/"+f_corr.replace("corr","tiles_per_frame")

				kill_procs()
				out_dir = "results_study/u"+str(user_id)+"_v"+str(video_id)+"_"+model+"/"
				os.system("mkdir "+out_dir)
				server_ip = run_server_and_get_ip(bw_trace_path,videoPath,args_server[model])
				time.sleep(1)

				client_cmd = "./bin/client "+user_frame_tiles_path+" "+user_frame_vp_path+" "+videoSizes+" "+videoPsnr+" "+displacementPath+" "+server_ip+" "
				if "Pano" in model:
					client_cmd += " /home/ehab/Desktop/Videos/Pano_tiles_grouping/v"+str(video_id)+"_grouping.txt" +" /home/ehab/Desktop/Videos/videos_bitrates/v"+str(video_id)+"_bitrates.txt "

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
	print("AUTOMATION MAIN_STUDY() BE CAREFUL!!!!")
	print("AUTOMATION MAIN_STUDY() BE CAREFUL!!!!")
	print("AUTOMATION MAIN_STUDY() BE CAREFUL!!!!")
	main()


	

		





