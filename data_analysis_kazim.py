from arducopter_extract.arducopter_extract import ArduLog
import pandas as pd
import glob
import numpy as np
import os
import pickle

def get_files():
    #files = glob.glob("/root/gdrive" + '/**/*.bin', recursive=True) + glob.glob("/root/gdrive" + '/**/*.BIN', recursive=True)
    files = glob.glob("/home/ntlhui/googledrive" + '/**/*.BIN', recursive=True)

    return files



def get_altitudes(files):

    field = 'GPS'
    field = 'AHR2'

    df_list = []
    for file in files:
        try:
            if field == 'GPS':
                poses = ArduLog(file).extract_6dof1()
                df = pd.DataFrame(poses, columns = ['TimeMS','Lat','Lng','RelAlt','T'])
                df = df[['TimeMS','RelAlt']].groupby(df.index // 5).agg({'TimeMS':'mean','RelAlt':'mean'})
                df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
                df.name = os.path.basename(file)    
                df_list.append(df)
            if field == 'AHR2':
                poses = ArduLog(file).extract_6dof3()
                df = pd.DataFrame(poses, columns = ['TimeMS','Roll','Pitch','Yaw','Alt','Lat','Lng'])
                df = df[['TimeMS','Alt']].groupby(df.index // 5).agg({'TimeMS':'mean','Alt':'mean'})
                df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
                df.name = os.path.basename(file)
                df_list.append(df)
        except KeyboardInterrupt:
            raise    
        except:
            pass
    
    return df_list


def get_dates(files):
    i = 1
    df = pd.DataFrame(columns = ['Flight Date','Number of Flights','Takeoff Times','Flight Durations'])
    for file in files:
        try:
            print(i)
            takeoffdate, takeoff_times, landing_times = ArduLog(file).extract_takeoffs()
            durations = [landing_time - takeoff_time for landing_time, takeoff_time in zip(landing_times,takeoff_times)]
            durations = [duration.total_seconds() for duration in durations]
            takeoff_times = [takeoff_time.strftime('%H:%M:%S') for takeoff_time in takeoff_times]
            #landing_times = [landing_time.strftime('%H:%M:%S') for landing_time in landing_times]
            df.loc[os.path.basename(file)] = [takeoffdate,len(takeoff_times),takeoff_times,durations]
            i+=1
        except KeyboardInterrupt:
            raise    
        except:
            pass
    return df

def get_currents(files):

    field = 'CURR'

    df_list = []
    for file in files:
        try:
            if field == 'CURR':
                poses = ArduLog(file).extract_current()
                df = pd.DataFrame(poses, columns = ['TimeMS','Curr'])
                df = df[['TimeMS','Curr']].groupby(df.index // 5).agg({'TimeMS':'mean','Curr':'mean'})
                df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
                df.name = os.path.basename(file)    
                df_list.append(df)
        except KeyboardInterrupt:
            raise    
        except:
            pass
    
    return df_list

def altitude_brackets(altitudes,currents):
    cond = 'Curr < 500'
    brackets = ['ground','mission']
    df_list = []
    for df_altitude, df_current in zip(altitudes,currents):
        df_current['cond'] = df_current.eval(cond)
        #grp.append(df_current.groupby('cond'))
        df_current['changed'] = df_current['cond'].ne(df_current['cond'].shift().bfill()).astype(int)
        grp = df_current.groupby('changed')
        try:
            changes = grp.get_group(1)
            prev = 0
            for index, row in changes.iterrows():
                df_altitude.loc[(df_altitude['TimeMS']>=prev)&(df_altitude['TimeMS']<row[0]),'bracket'] = brackets[index%2]
                prev = row[0]
            df_altitude.loc[df_altitude['TimeMS']>=prev,'bracket'] = 'ground'
            df_list.append(df_altitude)
        except:
            df_altitude['bracket'] = 'ground'
            df_list.append(df_altitude)
    return df_list



if __name__ == '__main__':
    files = get_files()
    df_altitudes = get_altitudes(files)
    with open('./data/altitudes.pkl') as f:
        pickle.dump(df_altitudes, f)
    df_takeoff = get_dates(files)
    df_takeoff.to_pickle("./data/dates.pkl")
  #  df_currents = get_currents(files[:3])
  #  df_brackets = altitude_brackets(df_altitudes,df_currents)