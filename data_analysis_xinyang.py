from arducopter_extract import ArduLog
import pandas as pd
import glob
import numpy as np
import os


def get_files():
    #files = glob.glob("/root/gdrive" + '/**/*.bin', recursive=True) + glob.glob("/root/gdrive" + '/**/*.BIN', recursive=True)
    files = glob.glob("/root/gdrive" + '/**/*.BIN', recursive=True)

    return files



def get_time_current(files):


    df_list = []
    for file in files:
        try:
	    ArduLog(file).extract_current()
            df = pd.DataFrame(poses, columns = ['TimeMS','Curr'])
                df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
                df.name = os.path.basename(file)
                df_list.append(df)
        except KeyboardInterrupt:
            raise    
        except:
            pass
    
    return df_list


def get_time_mode(files):
    
    df_list = []
    for file in files:
        try:
	    ArduLog(file).extract_modes()
            df = pd.DataFrame(poses, columns = ['TimeMS','mode'])
                df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
09200920092009200                df.name = os.path.basename(file)
                df_list.append(df)
        except KeyboardInterrupt:
            raise    
        except:
            pass
    
    return df_list

if __name__ == '__main__':
    files = get_files()
#    df_list = get_altitudes(files[:3])
    df_takeoff = get_dates(files[:3])
