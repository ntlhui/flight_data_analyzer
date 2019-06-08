from arducopter_extract.arducopter_extract import ArduLog
import pandas as pd
import glob
import numpy as np
import os
import pickle

def get_files():
    '''
    Searches through the Google Drive folder and returns the paths of .BIN files.
    Args:
        None
    Returns:
        files: (list(string)), List of paths
    '''
    #files = glob.glob("/root/gdrive" + '/**/*.bin', recursive=True) + glob.glob("/root/gdrive" + '/**/*.BIN', recursive=True)
    files = glob.glob("/root/gdrive" + '/**/*.BIN', recursive=True)

    return files



def get_altitudes(files):
    '''
    Extracts the altitudes from the log files given.
    Arg:
        files: (list(string)), List of paths
    Returns:
        df_list: (list(pd.Dataframe)), list of pandas dataframes that has 'Time' and 'Altitude' columns for each file in files.
    '''

    assert isinstance(files,list), "Files must be a 'list' of paths "
    assert all(isinstance(file,str) for file in files), "File paths should be string type"

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
    '''
    Extracts takeoff dates, number of fligts, takeoff times and takeoff durations from the log files given.
    Arg:
        files: (list(string)), List of paths
    Returns:
        df: (pd.Dataframe), Pandas dataframe that has 'Takeoff Date','Number of FLights', 
             Takeoff Times' and 'Flight Durations' columns for each file in files.
    '''
 
    assert isinstance(files,list), "Files must be a 'list' of paths "
    assert all(isinstance(file,str) for file in files), "File paths should be string type"
    
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
    '''
    Extracts current information from the log files given.
    Arg:
        files: (list(string)), List of paths
    Returns:
        df_list:  (list(pd.Dataframe)), list of pandas dataframes that has 'Time','Current' columns for each file in files.
    '''
    assert isinstance(files,list), "Files must be a 'list' of paths "
    assert all(isinstance(file,str) for file in files), "File paths should be string type"

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
    '''
    Extracts the altitudes and the state of the drone ('ground' or 'mission') from the log files given.
    Arg:
        altitudes: (list(pd.Dataframe)), List of dataframes of altitude information
        currents: (list(pd.Dataframe)), List of dataframes of current information
    Returns:
        df_list: (list(pd.Dataframe)), list of pandas dataframes that has 'Time' and 'Altitude', 'Bracket' columns for each file in files.
    '''

    assert isinstance(altitudes,list), "Altitudes input must be a 'list' of altitude dataframe "
    assert isinstance(currents,list), "Currents input must be a 'list' of current dataframe "

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

    # Main function to extract altitudes, takaoff information, current and altitude brackets.
 
    files = get_files()
    df_altitudes = get_altitudes(files)
    with open('./data/altitudes.pkl') as f:
        pickle.dump(df_altitudes, f)
    df_takeoff = get_dates(files)
    df_takeoff.to_pickle("./data/dates.pkl")
  #  df_currents = get_currents(files[:3])
  #  df_brackets = altitude_brackets(df_altitudes,df_currents)
