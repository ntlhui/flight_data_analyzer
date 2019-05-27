#!/usr/bin/env python3

import glob
import os
from arducopter_extract import arducopter_extract
from dji_extract import dji_extract
import numpy as np
import matplotlib.pyplot as plt; plt.ion()
from multiprocessing import Pool, Queue
from itertools import product

def process_ac(logfile, output_file):
	'''Processes the provided ArduCopter logfile and outputs the distance flown
	to the specified output file.

		Appends the following line to the output file:

		`'$s:%.0f\n' % (logfile, distance)`

	param:	logfile		Path to the ArduCopter binary log file
	param:	output_file	Path to the common output file
	'''
	if os.path.getsize(logfile) == 0:
		return
	log = arducopter_extract.ArduLog(logfile)
	try:
		positions_unfiltered = log.extract_6dof3()[:,(5, 6, 4)]
	except KeyError:
		badlogs = open('badlogs.txt', 'a')
		badlogs.write('%s\n' % (logfile))
		badlogs.close()
		return
	positions = []
	for i in range(len(positions_unfiltered)):
		if positions_unfiltered[i,0] != 0:
			positions.append(positions_unfiltered[i,:])
	if len(positions) == 0:
		return
	positions = np.array(positions)
	distances = np.zeros(len(positions) - 1)
	for i in range(len(distances)):
		distances[i] = np.linalg.norm(positions[i,:] - positions[i+1,:])
	distance = np.sum(distances)
	

	with open(output_file, 'a') as file:
		file.write('%s:%.0f\n' % (logfile, distance))

def process_dji(logfile, output_file):
	'''Processes the provided DJI logfile as a CVS and outputs the distance flown
	to the specified output file.

		Appends the following line to the output file:

		`'$s:%.0f\n' % (logfile, distance)`

	param:	logfile		Path to the DJI csv log file
	param:	output_file	Path to the common output file
	'''
	if os.path.getsize(logfile) == 0:
		return

	log = dji_extract.DJILog(logfile)
	try:
		positions_unfiltered = log.extract_6dof()
	except KeyError:
		badlogs = open('badlogs.txt', 'a')
		badlogs.write('%s\n' % (logfile))
		badlogs.close()
		return
	positions = []
	for i in range(len(positions_unfiltered)):
		if positions_unfiltered[i,0] != 0:
			positions.append(positions_unfiltered[i,(1,2,3)])
	if len(positions) == 0:
		return
	positions = np.array(positions)
	distances = np.zeros(len(positions) - 1)
	for i in range(len(distances)):
		distances[i] = np.linalg.norm(positions[i,:] - positions[i+1,:])
	distance = np.sum(distances)
	

	with open(output_file, 'a') as file:
		file.write('%s:%.0f\n' % (logfile, distance))
		

def plot_data(output_file):
	'''Plots the distance data in the provided output file as a histogram'''
	distance_map = {}
	with open(output_file) as file:
		for line in file:
			distance_map[line.split(':')[0]] = int(line.split(':')[1])
	distances = np.array(list(distance_map.values()))
	q_distances = np.round(distances / 100) * 100
	fig = plt.figure()
	plt.hist(q_distances)
	plt.xlabel('Distance (m)')
	plt.ylabel('Number of Flights')
	plt.title('Distribution of Flight Distances')
	return fig


if __name__ == '__main__':

	data_dir = '/home/ntlhui/googledrive'
	arducopterlogs = glob.glob(os.path.join(data_dir, "**", "*.BIN"), recursive=True) + glob.glob(os.path.join(data_dir, "**", "*.bin"), recursive=True)
	djilogs = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
	output_dir = '/home/ntlhui/workspace/ECE143/'

	output_file = os.path.join(output_dir, 'distances.csv')
	with open(output_file, 'w') as file:
		file.write("")

	p = Pool(7)
	process_ac_input = [(log, output_file) for log in arducopterlogs]
	process_dji_input = [(log, output_file) for log in djilogs]
	p.starmap(process_ac, process_ac_input)
	p.starmap(process_dji, process_dji_input)

	fig = plot_data(output_file)
	plt.figure(fig)
	plt.savefig('distance.png')
	plt.close(fig)
