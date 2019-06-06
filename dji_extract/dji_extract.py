#!/usr/bin/env python3

import numpy as np
import os
import mimetypes

def lc(path):
	'''Returns the number of lines in the specified file'''
	assert(os.path.isfile(path))
	assert(mimetypes.guess_type(path)[0] == 'text/csv')
	with open(path) as f:
		for i, l in enumerate(f):
			pass
	return i + 1

class DJILog(object):
	"""DJI Log CSV"""
	def __init__(self, path):
		super(DJILog, self).__init__()
		assert(os.path.isfile(path))
		assert(mimetypes.guess_type(path)[0] == 'text/csv')
		self.path = path

	def _not_empty(self, lst):
		'''Checks that all elements of the list of strings are nonempty'''
		assert(isinstance(lst, list))
		for element in lst:
			assert(isinstance(element, str))
			if element == '':
				return False
		return True

	def extract_fields(self, fields):
		with open(self.path) as csv_file:
			headers_arr = csv_file.readline().split(',')
			headers = {headers_arr[i]: i for i in range(len(headers_arr))}
			field_idx = [headers[field] for field in fields]
			extracted_data = []
			try:
				for line in csv_file:
					line_data = line.split(',')
					extracted_data.append([line_data[x] for x in field_idx])
			except:
				print(self.path)
		return extracted_data


	def extract_6dof(self):
		fields = ['offsetTime',
				  'IMU_ATTI(0):Longitude',
				  'IMU_ATTI(0):Latitude',
				  'General:relativeHeight',
				  'IMU_ATTI(0):roll',
				  'IMU_ATTI(0):pitch',
				  'IMU_ATTI(0):yaw']
		poses = self.extract_fields(fields)

		poses = [[float(i) for i in pose] for pose in poses if self._not_empty(pose)]

		return np.array(poses)

	def extract_vel(self):
		fields = ['offsetTime',
				  'IMU_ATTI(0):velN',
				  'IMU_ATTI(0):velE',
				  'IMU_ATTI(0):velD']
		str_velocities = self.extract_fields(fields)
		velocities = [[float(i) for i in v] for v in str_velocities if self._not_empty(v)]

		return np.array(velocities)

	def extract_rc(self):
		fields = ['offsetTime',
				  'RC:Throttle',
				  'RC:Rudder',
				  'RC:Elevator',
				  'RC:Aileron']
		rc_str = self.extract_fields(fields)
		rc = [[float(ch) for ch in t] for t in rc_str if self._not_empty(t)]
		return np.array(rc)

	def extract_modes(self):
		fields = ['offsetTime',
				  'RC:ModeSwitch']
		modes = self.extract_fields(fields)
		return np.array(modes)

	def extract_current(self):
		fields = ['offsetTime',
				  'BattInfo:Current']
		current_str = self.extract_fields(fields)
		current = [[float(x) for x in i] for i in current_str if self._not_empty(i)]
		return np.array(current)

	def extract_vel_current(self):
		'''Extracts the velocities and current for this log

		:returns	v	Timestamped velocities for this log in m/s as Vn, Ve, Vd
					c	Timestamped currents for this log
		'''
		fields = ['offsetTime', 'IMU_ATTI(0):velN', 'IMU_ATTI(0):velE', 
					'IMU_ATTI(0):velD', 'BattInfo:Current']
		v_list = self.extract_fields(fields[0:4])
		v = {int(float(v[0])):[float(x) for x in v[1:4]] for v in v_list if v[1] != '' and v[2] != '' and v[3] != ''}
		i_list = self.extract_fields([fields[0], fields[4]])
		c = {int(float(c[0])):float(c[1]) for c in i_list if c[1] != ''}
		return v, c

	def extract_times(self):
		fields = ['offsetTime',
				  'GPS:dateTimeStamp']
		datetime = self.extract_fields(fields)
		return datetime

		
if __name__ == '__main__':
	path = 'FLY034.csv'
	log = DJILog(path)
	poses = log.extract_6dof()
	velocities = log.extract_vel()
	rc = log.extract_rc()
	modes = log.extract_modes()
	currents = log.extract_current()