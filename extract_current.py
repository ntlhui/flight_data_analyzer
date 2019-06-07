#!/usr/bin/env python3

from arducopter_extract.arducopter_extract import ArduLog
from arducopter_extract.arducopter_extract import ACFT
from dji_extract.dji_extract import DJILog
import numpy as np
import glob
import os
from multiprocessing import Pool
import pandas as pd
import pickle

def extract_vel_current(logfile):
	if os.path.getsize(logfile) == 0:
		return None
	if os.path.splitext(logfile)[1].lower() == '.bin':
		retval = extract_vel_current_APM(logfile)
		if retval is None:
			return None
		v3, c = retval
	if os.path.splitext(logfile)[1].lower() == '.csv':
		v3, c = extract_vel_current_DJI(logfile)
	v = {key:np.linalg.norm(np.array(vel[0:2])) for key, vel in v3.items()}
	return {key:[v[key], c[key]] for key in set(v.keys()).intersection(c.keys())}

def extract_vel_current_APM(logfile):
	logstruct = ArduLog(logfile)
	if logstruct.getType() != ACFT.SOLO:
		return None
	try:
		v, c = logstruct.extract_vel_current()
	except:
		print(logfile)
		return None
	return v, c

def extract_vel_current_DJI(logfile):
	logstruct = DJILog(logfile)
	v, c = logstruct.extract_vel_current()
	return v, c

if __name__ == '__main__':
	data_dir = '/home/ntlhui/googledrive'
	arducopterlogs = glob.glob(os.path.join(data_dir, "**", "*.BIN"), recursive=True) + glob.glob(os.path.join(data_dir, "**", "*.bin"), recursive=True)
	djilogs = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
	# all_logs = djilogs
	all_logs = arducopterlogs

	p = Pool(7)
	results = p.map(extract_vel_current, all_logs)
	with open('data/solo_vel_cur.pkl', 'wb') as f:
		pickle.dump(results, f)