import os
import numpy as np
import sys

BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
BITS_IN_BYTE = 8.0



#This will take one value which is single bandwidth value to mimic. 

#python con.. <Bandwidth in mbps>

def main():

			if len(sys.argv)!=2:
				print("Usage: <BW value>")
				sys.exit(1)

			bytes_recv = []
			recv_time = []
			mf=open("trace_mahimahi_"+sys.argv[1]+"mbps.txt", 'w')

			bytes_recv.append((float(sys.argv[1])*1024*1024)/8)
			recv_time.append(float(1000))
			bytes_recv = np.array(bytes_recv)
			recv_time = np.array(recv_time)

			throughput_all = bytes_recv / recv_time
			millisec_time = 0
			for i in range(len(throughput_all)):

				throughput = throughput_all[i]
				
				pkt_per_millisec = throughput / BYTES_PER_PKT 

				millisec_count = 0
				pkt_count = 0

				while True:
					millisec_count += 1
					millisec_time += 1
					to_send = (millisec_count * pkt_per_millisec) - pkt_count
					to_send = np.floor(to_send)

					for i in range(int(to_send)):

						mf.write(str(millisec_time) + "\n")

					pkt_count += to_send

					if millisec_count > recv_time[0]:
						break


if __name__ == '__main__':
	main()
