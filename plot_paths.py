#!/usr/bin/env python3

from arducopter_extract import arducopter_extract
from dji_extract import dji_extract
import shapefile
import os
import glob
import numpy as np
from multiprocessing import Pool

import argparse

def plot_ardupath(log, output_filename, overwrite = False):
	'''Plots the specified ArduCopter log as an ESRI shapefile at the specified
	output path.

	param:	log				ArduCopter binary log file path
	param:	output_filename	Output path
	'''
	if os.path.getsize(log) == 0:
		return
	if os.path.isfile("%s.shp" % (os.path.splitext(output_filename)[0])) and not overwrite:
		return
	logstruct = arducopter_extract.ArduLog(log)
	try:
		positions_unfiltered = logstruct.extract_6dof3()[:,(5, 6, 4)]
	except KeyError:
		badlogs = open('badlogs.txt', 'a')
		badlogs.write('%s\n' % (log))
		badlogs.close()
		return
	positions = []
	for i in range(len(positions_unfiltered)):
		if positions_unfiltered[i,0] != 0:
			positions.append(positions_unfiltered[i,:])
	if len(positions) == 0:
		return
	
	coords = [[position[1], position[0]] for position in positions]
	alts = [position[2] for position in positions]

	writer = shapefile.Writer(output_filename)
	writer.field('log', 'C')
	writer.line([coords])
	writer.record(log)
	writer.close()
	proj = open("%s.prj" % (os.path.splitext(output_filename)[0]), 'w')
	epsg1 = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
	proj.write(epsg1)
	proj.close()

def plot_djipath(log, output_filename, overwrite = False):
	'''Plots the specified DJI log as an ESRI shapefile at the specified
	output path.

	param:	log				DJI binary log file path
	param:	output_filename	Output path
	'''
	if os.path.getsize(log) == 0:
		return
	if os.path.isfile("%s.shp" % (os.path.splitext(output_filename)[0])) and not overwrite:
		return
	logstruct = dji_extract.DJILog(log)
	try:
		positions_unfiltered = logstruct.extract_6dof()
	except KeyError:
		badlogs = open('badlogs.txt', 'a')
		badlogs.write('%s\n' % (logfile))
		badlogs.close()
		return
	positions = []
	for i in range(len(positions_unfiltered)):
		if positions_unfiltered[i,0] != 0:
			positions.append(positions_unfiltered[i,(2,1,3)])
	if len(positions) == 0:
		return
	coords = [list(position[0:2]) for position in positions]
	alts = [position[2] for position in positions]

	writer = shapefile.Writer(output_filename)
	writer.field('log', 'C')
	writer.line([coords])
	writer.record(log)
	writer.close()
	proj = open("%s.prj" % (os.path.splitext(output_filename)[0]), 'w')
	epsg1 = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
	proj.write(epsg1)
	proj.close()



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Plots the flight paths of the given flight logs')
	parser.add_argument('--input_dir', '-i', dest='data_dir', help='Directory containing all flight logs to process', default='/home/ntlhui/googledrive')
	parser.add_argument('--output_dir', '-o', dest='output_dir', help='Directory to store all shapefiles in', default='/home/ntlhui/workspace/ECE143/paths')
	args = parser.parse_args()

	data_dir = args.data_dir
	arducopterlogs = glob.glob(os.path.join(data_dir, "**", "*.BIN"), recursive=True) + glob.glob(os.path.join(data_dir, "**", "*.bin"), recursive=True)
	djilogs = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
	output_dir = args.output_dir

	overwrite = True

	output_filenames = set()

	arduprocess_input = []

	for log in arducopterlogs:
		output_filename = os.path.join(output_dir, os.path.basename(log))
		if output_filename not in output_filenames:
			output_filenames.add(output_filename)
		else:
			# name collision
			i = 1
			for i in range(1, len(arducopterlogs)):
				output_filename = os.path.join(output_dir, "%s-%d%s" % (os.path.splitext(os.path.basename(log))[0], i, os.path.splitext(os.path.basename(log))[1]))
				if output_filename not in output_filenames:
					output_filenames.add(output_filename)
					break
		arduprocess_input.append([log, output_filename, overwrite])

	djiprocess_input = []
	
	for log in djilogs:
		output_filename = os.path.join(output_dir, os.path.basename(log))
		if output_filename not in output_filenames:
			output_filenames.add(output_filename)
		else:
			# name collision
			i = 1
			for i in range(1, len(arducopterlogs)):
				output_filename = os.path.join(output_dir, "%s-%d%s" % (os.path.splitext(os.path.basename(log))[0], i, os.path.splitext(os.path.basename(log))[1]))
				if output_filename not in output_filenames:
					output_filenames.add(output_filename)
					break
		djiprocess_input.append([log, output_filename, overwrite])

	p = Pool(7)
	print("Processing Arducopter Logs")
	p.starmap(plot_ardupath, arduprocess_input)
	print("Processing DJI Logs")
	p.starmap(plot_djipath, djiprocess_input)



