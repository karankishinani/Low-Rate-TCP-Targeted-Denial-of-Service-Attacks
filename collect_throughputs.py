import re
import os
import shutil
from os import path

OUTPUT_DIR = 'outputs'

def collect_throughputs(filepath):
	str = 'data-q4-p0.75-i1/iperf_out.txt'
	matchfile = re.search('data-q([0-9]+)-p([0-9\.]+)', str)
	qsize = int(matchfile.group(1))
	period = float(matchfile.group(2))

	# Getting average throughput from the file
	with open(filepath) as input_f:
		lines = input_f.readlines()

		if len(lines) == 0:
			print("Error: {} is empty".format(filepath))
			return

		# Last line of the output contains the average throughput over the whole time period.
		# Bits/Bytes can be in Kilo/Mega. Has format:
		# [ ID] Interval     Transfer     Bandwidth
		# [ 17] 0.0-2.0 sec  96.0 KBytes  393 Kbits/sec
		#  ...
		# [ 17] 0.0-30.0 sec 384  KBytes  98.9 Kbits/sec
		last_line = lines[-1]
		matchoutput = re.search('(?<=Bytes)[0-9\.\ ]+', last_line)
		if ' 0.0' not in last_line or matchoutput is None:
			print("Error: last line does not seem to match average throughput format")
			return

		if 'Mbits' in last_line:
			throughput = float(matchoutput.group(0))
		elif 'Kbits' in last_line:
			throughput = float(matchoutput.group(0)) / 1024
		elif 'bits' in last_line:
			throughput = float(matchoutput.group(0)) / 1024 / 1024
		print(throughput)

	# Appending throughput into a file for the same qsize. Period and throughput(Mbits/sec) delimited by space
	output_filepath = path.join(OUTPUT_DIR, 'outq{}.txt'.format(qsize))
	with open(output_filepath, 'a+') as output_f:
		output_f.write('{} {}'.format(period, throughput))


if __name__ == '__main__':
	# Reset outputs dir
	if path.exists(OUTPUT_DIR):
		shutil.rmtree(OUTPUT_DIR)
	os.mkdir(OUTPUT_DIR)

	# Look for iperf outputs in directories
	for dir, _, _ in os.walk('.'):
		prospective_file = path.join(dir, 'iperf_out.txt')
		if path.exists(prospective_file):
			collect_throughputs(prospective_file)