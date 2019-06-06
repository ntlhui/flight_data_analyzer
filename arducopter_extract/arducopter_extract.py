#!/usr/bin/env python3

import numpy as np
import os
import mimetypes
from pymavlink import mavutil
from pymavlink.dialects.v10 import ardupilotmega as mavlink
import argparse
import datetime
from enum import Enum
import csv
from dateutil.tz import tzlocal
import pytz

class ACFT(Enum):
    UNKNOWN = -1
    SOLO    = 0
    PX4     = 1

class ArduLog(object):
	"""
	Arducopter parse from log file
	"""
	def __init__(self, path):
		super(ArduLog, self).__init__()
		assert(os.path.isfile(path))
		#assert(mimetypes.guess_type(path)[0] == 'log')
		self.path = path
		self.acft = ACFT.SOLO


	def leap(self,date):
		"""
		Return the number of leap seconds since 6/Jan/1980
		:param date: datetime instance
		:return: leap seconds for the date (int)
		"""
		if date < datetime.datetime(1981, 6, 30, 23, 59, 59):
			return 0
		leap_list = [(1981, 6, 30), (1982, 6, 30), (1983, 6, 30),
					(1985, 6, 30), (1987, 12, 31), (1989, 12, 31),
					(1990, 12, 31), (1992, 6, 30), (1993, 6, 30),
					(1994, 6, 30), (1995, 12, 31), (1997, 6, 30),
					(1998, 12, 31), (2005, 12, 31), (2008, 12, 31),
					(2012, 6, 30), (2015, 6, 30), (2016, 12, 31)]
		leap_dates = list(map(lambda x: datetime.datetime(x[0], x[1], x[2], 23, 59, 59),
						leap_list))
		for j in range(len(leap_dates[:-1])):
			if leap_dates[j] < date < leap_dates[j + 1]:
				return j + 1
		return len(leap_dates)

	def extract_6dof1(self):
		self.mav_master = mavutil.mavlink_connection(self.path)

		poses = []
		pose = []
		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'MSG':
				version = msg.to_dict()['Message'].split()[1]
				if version == 'solo-1.3.1':
					self.acft = ACFT.SOLO
					GPS_fields = ['TimeMS',
						  'Lat',
						  'Lng',
						  'RelAlt',
						  'T']
				elif version == 'V3.3.3':
					self.acft = ACFT.PX4
					GPS_fields = ['GMS',
						  'Lat',
						  'Lng',
						  'RelAlt',
						  'TimeUS']
			if msg.get_type() == 'GPS':
				pose = [msg.to_dict()[x] for x in GPS_fields]
				poses.append(pose)    
		return np.array(poses)        

	def extract_6dof2(self):
		self.mav_master = mavutil.mavlink_connection(self.path)
		ATT_fields = ['TimeMS',
					  'Roll',
					  'Pitch',
					  'Yaw']	

		poses = []
		pose = []
		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'ATT':
				pose = [msg.to_dict()[x] for x in ATT_fields]
				poses.append(pose)    
		return np.array(poses)   
	

	def extract_6dof3(self):
		self.mav_master = mavutil.mavlink_connection(self.path)
		AHR2_fields = ['TimeMS',
					   'Roll',
					   'Pitch',
					   'Yaw',
					   'Alt',
					   'Lat',
					   'Lng']

		poses = []
		pose = []
		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'AHR2':
				pose = [msg.to_dict()[x] for x in AHR2_fields]
				poses.append(pose)    
		return np.array(poses)

	def extract_vel(self):
		self.mav_master = mavutil.mavlink_connection(self.path)
		EKF1_fields = ['TimeMS',
				  	   'VN',
				       'VE',
				       'VD']
		velocities = []
		velocity = []
		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'EKF1':
				velocity = [msg.to_dict()[x] for x in EKF1_fields]
				velocities.append(velocity)    
		return np.array(velocities)


	def extract_current(self):
		self.mav_master = mavutil.mavlink_connection(self.path)
		CURR_fields = ['TimeMS',
				  	   'Curr']
		currents = []
		current = []
		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'CURR':
				current = [msg.to_dict()[x] for x in CURR_fields]
				currents.append(current)    
		return np.array(currents)

	def extract_vel_current(self):
		'''Returns the velocities and currents from this logfile

		:returns	v	Dictionary of timestamped velocities Vn, Ve, Vd
					c	Dictionary of timestamped current draw
		'''
		self.mav_master = mavutil.mavlink_connection(self.path)
		fields = ['TimeMS', 'VN', 'VE', 'VD', 'Curr']

		v = {}
		c = {}
		scale = 1e-3
		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'MSG':
				version = msg.to_dict()['Message'].split()[1]
				if version == 'solo-1.3.1':
					self.acft = ACFT.SOLO
				elif version == 'V3.3.3':
					self.acft = ACFT.PX4
					fields[0] = 'TimeUS'
					scale = 1e-6
			if msg.get_type() == 'EKF1':
				v[int(msg.to_dict()[fields[0]] * scale)] = [msg.to_dict()[x] for x in fields[1:4]]
			if msg.get_type() == 'CURR':
				c[int(msg.to_dict()[fields[0]] * scale)] = msg.to_dict()[fields[4]]
		return v, c


	def extract_modes(self):
		self.mav_master = mavutil.mavlink_connection(self.path)
		MODE_fields = ['TimeMS',
					   'Mode']
		modes = []
		mode = []
		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'MODE':
				mode = [msg.to_dict()[x] for x in MODE_fields]
				modes.append(mode)    
		return np.array(modes)

	def extract_takeoffs(self):
		self.mav_master = mavutil.mavlink_connection(self.path)
		takeoff_times = []
		landing_times = []
		errors = []
		takeoffWithoutGPS = 0
		takeoff_seq = []
		landing_seq = []
		seqNum = 0
		prevCurr = -1
		flying = False
		lastGPS = -1
		timeInAir = 0

		while True:
			msg = self.mav_master.recv_match(blocking = False)
			if msg is None:
				break
			if msg.get_type() == 'MSG':
				version = msg.to_dict()['Message'].split()[1]
				if version == 'solo-1.3.1':
					self.acft = ACFT.SOLO
				elif version == 'V3.3.3':
					self.acft = ACFT.PX4

			if msg.get_type() == 'GPS':
				if msg.to_dict()['Status'] >= 3:
					if self.acft == ACFT.SOLO:
						gps_time = int(msg.to_dict()['TimeMS'])
						gps_week = int(msg.to_dict()['Week'])
						apm_time = int(msg.to_dict()['T'])
					elif self.acft == ACFT.PX4:
						gps_time = int(msg.to_dict()['GMS'])
						gps_week = int(msg.to_dict()['GWk'])
						apm_time = int(msg.to_dict()['TimeUS']) / 1e3
					offset = gps_time - apm_time
					lastGPS = seqNum
			if msg.get_type() == 'CURR':
				if int(msg.to_dict()['Curr']) > 500:
					flying = True

					if self.acft == ACFT.SOLO:
						msgtimestamp = int(msg.to_dict()['TimeMS'])
					elif self.acft == ACFT.PX4:
						msgtimestamp = int(msg.to_dict()['TimeUS']) / 1e3

					if prevCurr != -1:
						timeInAir = timeInAir + msgtimestamp - prevCurr
						prevCurr = msgtimestamp
					else:
						prevCurr = msgtimestamp
						if lastGPS != -1:
							secs_in_week = 604800
							gps_epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)
							date_before_leaps = (gps_epoch + datetime.timedelta(
								seconds = gps_week * secs_in_week + (prevCurr + 
								offset) / 1e3))
							date = (date_before_leaps - datetime.timedelta(seconds = 
								self.leap(date_before_leaps)))
							# print("Takeoff at %s UTC" % (date.strftime('%Y-%m-%d %H:%M:%S')))
							takeoff_seq.append(lastGPS)
							takeoff_times.append(date)
						else:
							# print("Takeoff without GPS fix!")
							takeoffWithoutGPS = takeoffWithoutGPS + 1
				else:
					flying = False
					if prevCurr != -1:
						if lastGPS != -1:
							secs_in_week = 604800
							gps_epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)
							date_before_leaps = (gps_epoch + datetime.timedelta(
								seconds = gps_week * secs_in_week + (prevCurr + 
								offset) / 1e3))
							date = (date_before_leaps - datetime.timedelta(seconds = 
								self.leap(date_before_leaps)))
							# print("Takeoff at %s UTC" % (date.strftime('%Y-%m-%d %H:%M:%S')))
							landing_seq.append(lastGPS)
							landing_times.append(date)
						else:
							landing_seq.append(seqNum)
					prevCurr = -1
			seqNum = seqNum + 1
		timeInAir = timeInAir / 1e3 / 60 / 60
		if len(takeoff_times) == 0:
			takeoff_date = None
		else:
			takeoff_date = pytz.utc.localize(takeoff_times[0]).astimezone(tzlocal()).date()

		return takeoff_date,takeoff_times,landing_times


if __name__ == '__main__':
	path = '423.BIN'
	log = ArduLog(path)
	# poses1 = log.extract_6dof1()
	# poses2 = log.extract_6dof2()
	# poses3 = log.extract_6dof3()
	# velocities = log.extract_vel()
	# currents = log.extract_current()
	takeoff = log.extract_takeoffs()