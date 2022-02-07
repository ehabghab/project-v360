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
def run_server_and_get_ip(tracefile):
	
	interfaces_cmd = "ls /sys/class/net/"
	pid1 = subprocess.Popen(shlex.split(interfaces_cmd), stdout=subprocess.PIPE, shell=False)
	interfaces_before_mahimahi, err1 = pid1.communicate()

	#mahimahi_preq_cmd = "sudo sysctl -w net.ipv4.ip_forward=1"
	#pid2 = subprocess.Popen(shlex.split(mahimahi_preq_cmd), stdout=subprocess.PIPE, shell=False)
	#out2, err2 = pid2.communicate()

	#This will create mahimahi with http-server @ port 7717 inside mahimahi shell"
	mahimahi_cmd = "mm-link "+tracefile+" "+tracefile+" ./bin/server"
	pid3 = subprocess.Popen(mahimahi_cmd,shell=True)

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

	user_trace_dir = "../split/"
	tile_size ="quality_tile_sizes.txt"
	user_tile_per_frame_traces = ["tiles_per_frame_user_3.txt"]#["tiles_per_frame_synthetic_user_1.txt","tiles_per_frame_user_3.txt","tiles_per_frame_user_13.txt"]#,"tiles_per_frame_user_29.txt"]
	#user_vp_corr_per_frame_traces = ["vp_corr_per_frame_user_3.txt"S,"vp_corr_per_frame_user_13.txt","vp_corr_per_frame_user_29.txt"]
	bw_trace_dir = "/home/ehab/Desktop/Project-V360/automate/"        
	bw_traces = ["trace_mahimahi_3.1mbps.txt","trace_mahimahi_4.8mbps.txt","trace_mahimahi_5.5mbps.txt","trace_mahimahi_6.2mbps.txt","trace_mahimahi_10mbps.txt"]
	delays = [0]	
	out_file = open("exp_log.txt","w")
	for bw_trace in bw_traces:
		for user_tile_trace in user_tile_per_frame_traces:
			user_id = user_tile_trace.split("_")[4].split(".")[0]
			vp_corr_trace = "vp_corr_per_frame_user_"+user_id+".txt"
			if "tiles_per_frame_synthetic_user_1" in user_tile_trace:
				vp_corr_trace = "vp_corr_per_frame_synthetic_user_1.txt"
			kill_procs()
			for delay in delays:
				out_file.write(bw_trace+"\n"+str(delay)+"\n"+user_tile_trace+"\n=========\n")
				server_ip = run_server_and_get_ip(bw_trace_dir+bw_trace)
				time.sleep(2)
				client_cmd = "mm-delay "+str(delay)+" ./bin/client "+user_trace_dir+user_tile_trace+" "+user_trace_dir+vp_corr_trace+" "+user_trace_dir+tile_size+" "+server_ip
				pid = subprocess.Popen(client_cmd,shell=True)
				try:	
					signal.alarm(15*60)
					out,err = pid.communicate()
					print(err)
					print(out)
				except :
					print("TIME out")
				kill_procs()
				time.sleep(5)


if __name__ == "__main__":
	main()


	

		





