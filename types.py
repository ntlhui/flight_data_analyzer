#!/usr/bin/env python3
import glob
from dji_extract import dji_extract
from arducopter_extract import arducopter_extract
import os
import pickle
import matplotlib.pyplot as plt; plt.ion()
from multiprocessing import Pool

def process(logfile):
	'''Processes the given logfile for the aircraft type and number of takeoffs

	:returns	acft	Aircraft type as string.  One of SOLO, PX4, S1000, or DJI
				tofs	Number of takeoffs
	'''
	if os.path.getsize(logfile) == 0:
		return None
	if os.path.splitext(logfile)[1].lower() == '.bin':
		retval = extract_takeoffs_apm(logfile)
		if retval is None:
			return None
		acft, tofs = retval
	if os.path.splitext(logfile)[1].lower() == '.csv':
		acft, tofs = extract_takeoffs_dji(logfile)
	return acft, tofs

def extract_takeoffs_apm(logfile):
	'''Processes the given APM logfile for the aircraft type and number of takeoffs

	:returns	acft	Aircraft type as string.  One of SOLO, PX4, or S1000
				tofs	Number of takeoffs
	'''
	log_struct = arducopter_extract.ArduLog(logfile)
	acft = log_struct.getType()
	if acft == arducopter_extract.ACFT.SOLO:
		acft_str = 'SOLO'
	elif acft == arducopter_extract.ACFT.PX4:
		acft_str = 'PX4'
	elif acft == arducopter_extract.ACFT.S1000:
		acft_str = 'S1000'
	else:
		acft_str = 'UNKNOWN'
		print("%s: Unknown aircraft" % (logfile))
	retval = log_struct.extract_takeoffs()
	if retval is None:
		return None
	takeoff_date,takeoff_times,landing_times = retval
	return acft_str, len(takeoff_times)

def extract_takeoffs_dji(logfile):
	'''Processes the given DJI logfile for the aircraft type and number of takeoffs

	:returns	acft	Aircraft type as string as DJI
				tofs	Number of takeoffs
	'''
	log_struct = dji_extract.DJILog(logfile)
	acft_str = 'DJI'
	tofs = log_struct.get_takeoffs()
	return acft_str, tofs

if __name__ == '__main__':
	data_dir = '/home/ntlhui/googledrive'
	all_logs = glob.glob(os.path.join(data_dir, '**', '*.BIN'), recursive=True) + \
			   glob.glob(os.path.join(data_dir, '**', '*.bin'), recursive=True) + \
			   glob.glob(os.path.join(data_dir, '**', '*.csv'), recursive=True)

	p = Pool(7)
	retval = p.map(process, all_logs)
	with open('data/types.pkl', 'wb') as f:
		pickle.dump(retval, f)