#!/usr/bin/env python3

import glob
import os
from arducopter_extract import arducopter_extract
from dji_extract import dji_extract
import numpy as np
import matplotlib.pyplot as plt; plt.ion()
from multiprocessing import Pool
from itertools import product
import utm
import cv2
import argparse
import ipython_bell
import shapefile

def invert_tf(tf):
	'''Inverts a SE3 transform'''
	assert(isinstance(tf, np.ndarray))
	assert(tf.shape == (3, 3))
	Rinv = np.linalg.inv(tf[0:2,0:2])
	affine = -1*np.matmul(Rinv, tf[0:2,2]).reshape((2, 1))
	wTm = np.block([[Rinv, affine], [0, 0, 1]])
	return wTm

def parallel_extents(logfile, output):
	'''Outputs get extents to the outut file'''
	extents = get_extents(logfile)
	if extents is None:
		return
	with open(output, 'a') as file:
		file.write("%s:%.6f,%.6f;%.6f,%.6f;%.6f,%.6f;%.6f,%.6f\n" % (logfile, 
			extents[0][0], extents[0][1], extents[1][0], extents[1][1], 
			extents[2][0], extents[2][1], extents[3][0], extents[3][1]))

def get_extents(logfile):
	'''Plots the extents of the specified logfile'''
	if os.path.getsize(logfile) == 0:
		return
	if os.path.splitext(logfile)[1].lower() == '.bin':
		logstruct = arducopter_extract.ArduLog(logfile)
		try:
			positions_unfiltered = logstruct.extract_6dof3()[:,(5, 6, 4)] #x, y, -z
		except KeyError:
			badlogs = open('badlogs.txt', 'a')
			badlogs.write('%s\n' % (logfile))
			badlogs.close()
			return
	elif os.path.splitext(logfile)[1].lower() == '.csv':
		logstruct = dji_extract.DJILog(logfile)
		positions_unfiltered = logstruct.extract_6dof()
		if positions_unfiltered is None:
			return
		positions_unfiltered = np.array([[position[2], position[1], position[3]] for position in positions_unfiltered])
	positions = []
	utm_zone = 'Z'
	utm_zonenum = 0
	for i in range(len(positions_unfiltered)):
		if positions_unfiltered[i, 0] != 0 and positions_unfiltered[i, 1] != 0:
			utm_coord = utm.from_latlon(positions_unfiltered[i, 0], positions_unfiltered[i, 1])
			positions.append([utm_coord[0], utm_coord[1], positions_unfiltered[i, 2]])
			utm_zonenum = utm_coord[2]
			utm_zone = utm_coord[3]
	if len(positions) == 0:
		return
	np_positions = np.array(positions)
	min_coords = np.amin(np_positions, 0)
	max_coords = np.amax(np_positions, 0)
	coord_range = max_coords - min_coords
	scale = 0.1
	pos_map = np.zeros((int(coord_range[0] * scale) + 1, int(coord_range[1] * scale) + 1), dtype=np.uint8)
	mTw = np.array([[scale, 0, -scale * min_coords[0]],
					[0, scale, -scale * min_coords[1]],
					[0, 0, 1]])
	world_pos = np.vstack((np_positions[:,0:2].transpose(), np.ones(np_positions.shape[0])))
	map_pos = np.floor(np.matmul(mTw, world_pos))
	for i in range(map_pos.shape[1] - 1):
		 cv2.line(pos_map, (int(map_pos[0, i]), int(map_pos[1, i])), (int(map_pos[0, i+1]), int(map_pos[1, i+1])), 255)
	contours, hierarchy = cv2.findContours(pos_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	rect = cv2.boundingRect(contours[0])
	box = np.array([[rect[0], rect[0], rect[0] + rect[2], rect[0] + rect[2]],
					[rect[1], rect[1] + rect[3], rect[1], rect[1] + rect[3]],
					[1, 1, 1, 1]])
	wTm = invert_tf(mTw)
	box_world = np.matmul(wTm, box)

	extents = []

	for i in range(box_world.shape[1]):
		ll_coord = utm.to_latlon(box_world[0, i], box_world[1, i], utm_zonenum, utm_zone)
		extents.append(ll_coord)

	return extents

def check_overlap(rect1, rect2):
	'''Checks if the specified rectangles overlap'''
	assert(isinstance(rect1, np.ndarray))
	assert(isinstance(rect2, np.ndarray))
	assert(rect1.shape == (4, 2))
	assert(rect2.shape == (4, 2))
	assert(np.issubdtype(rect1.dtype, np.number))
	assert(np.issubdtype(rect2.dtype, np.number))

	r1_min = np.amin(rect1, 0)
	r1_max = np.amax(rect1, 0)
	r2_min = np.amin(rect2, 0)
	r2_max = np.amax(rect2, 0)

	if r1_min[0] > r2_max[0] or r2_min[0] > r1_max[0]:
		return False
	if r1_min[1] > r2_max[1] or r2_min[1] > r2_max[1]:
		return False
	return True

def combine_area(rect1, rect2):
	''' Combines the two rectangles to max extents'''
	assert(isinstance(rect1, np.ndarray))
	assert(isinstance(rect2, np.ndarray))
	assert(rect1.shape == (4, 2))
	assert(rect2.shape == (4, 2))
	assert(np.issubdtype(rect1.dtype, np.number))
	assert(np.issubdtype(rect2.dtype, np.number))

	r1_min = np.amin(rect1, 0)
	r1_max = np.amax(rect1, 0)
	r2_min = np.amin(rect2, 0)
	r2_max = np.amax(rect2, 0)

	gb_min = np.amin([r1_min, r2_min], 0)
	gb_max = np.amax([r1_max, r2_max], 0)
	return np.array([gb_min,
					[gb_min[0], gb_max[1]],
					gb_max,
					[gb_max[0], gb_min[0]]])

def reorder_extent(rect1):
	''' Sorts extent corners into clockwise direction'''
	assert(isinstance(rect1, np.ndarray))
	assert(rect1.shape == (4, 2))
	assert(np.issubdtype(rect1.dtype, np.number))
	r1_min = np.amin(rect1, 0)
	r1_max = np.amax(rect1, 0)
	return np.array([r1_min,
					[r1_min[0], r1_max[1]],
					r1_max,
					[r1_max[0], r1_min[1]]])

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Plots the extents of flight areas in the specified logs')
	parser.add_argument('--input_dir', '-i', metavar='input_dir', help='Directory containing logs', default='/root/gdrive')
	parser.add_argument('--output_file', '-o', metavar='output_file', help='Path to extents filename', default='./flight_areas.shp')

	args = parser.parse_args()

	data_dir = args.input_dir
	arducopterlogs = glob.glob(os.path.join(data_dir, "**", "*.BIN"), recursive=True) + glob.glob(os.path.join(data_dir, "**", "*.bin"), recursive=True)
	djilogs = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
	output_dir = '/tmp/'

	all_extents = []

	all_logs = arducopterlogs + djilogs
	output_file = '/tmp/extents.csv'
	if os.path.isfile(output_file):
		os.remove(output_file)

	parallel_logs = [(log, output_file) for log in all_logs]

	# for log in all_logs:
	# 	extent = get_extents(log)
	# 	if extent is None:
	# 		continue
	# 	all_extents += extent
	p = Pool(7)
	p.starmap(parallel_extents, parallel_logs)
	# for log in parallel_logs:
	# 	print(log[0])
	# 	parallel_extents(log[0], log[1])

	with open(output_file) as extents_file:
		for line in extents_file:
			logfile = line.strip().split(':')
			raw_extents = line.strip().split(':')[1].split(';')
			extents = [(float(coord.split(',')[0]), float(coord.split(',')[1])) for coord in raw_extents]
			all_extents += [extents]

	np.save('flight_extents.npy', all_extents)

	flight_areas = []

	for lextent in all_extents:
		found_overlap = False
		extent = np.array(lextent)
		for flight_area in flight_areas:
			if check_overlap(extent, flight_area):
				flight_area = combine_area(extent, flight_area)
				found_overlap = True
				break
		if not found_overlap:
			flight_areas.append(reorder_extent(extent))
		if found_overlap:
			area_remove = []
			for i in range(len(flight_areas)):
				if flight_area is flight_areas[i]:
					continue
				else:
					if check_overlap(flight_area, flight_areas[i]):
						flight_area = combine_area(flight_area, flight_areas[i])
						area_remove.append(i)
			flight_areas = [flight_areas[i] for i in range(len(flight_areas)) if i not in area_remove]

	writer = shapefile.Writer(args.output_file)
	writer.field('sequence', 'N')
	for i in range(len(flight_areas)):
		writer.poly([flight_areas[i][:,(1, 0)].tolist()])
		writer.record(i + 1)
	writer.close()
	proj = open("%s.prj" % (os.path.splitext(args.output_file)[0]), 'w')
	epsg1 = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
	proj.write(epsg1)
	proj.close()

	writer = shapefile.Writer("%s_point" % os.path.splitext(args.output_file)[0])
	writer.field('sequence', 'N')
	for i in range(len(flight_areas)):
		writer.point(flight_areas[i][0,1], flight_areas[i][0, 0])
		writer.record(i+1)
	writer.close()
	proj = open("%s_point.prj" % (os.path.splitext(args.output_file)[0]), 'w')
	epsg1 = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
	proj.write(epsg1)
	proj.close()
