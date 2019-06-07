from arducopter_extract import ArduLog
import pandas as pd
import glob
import numpy as np
import os
import pandas as pd
import glob
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy as np
from pandas import Series, DataFrame
import pylab

def get_files():
    #files = glob.glob("/root/gdrive" + '/**/*.bin', recursive=True) + glob.glob("/root/gdrive" + '/**/*.BIN', recursive=True)
    files = glob.glob("/root/gdrive" + '/**/*.BIN', recursive=True)

    return files



def get_time_current(files):

    df_list = []
    for file in files:
        try:
            times = ArduLog(file).extract_current()
            df = pd.DataFrame(times, columns = ['TimeMS','curr'])
            df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
            df.name = os.path.basename(file)
            df_list.append(df)
        except KeyboardInterrupt:
            raise    
        except:
            pass
    
    return df_list


# def get_time_mode(files):
    
#     df_list = []
#     for file in files:
#         try:
#             times = ArduLog(file).extract_modes()
#             df = pd.DataFrame(times, columns = ['TimeMS','mode'])
#             df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
#             df.name = os.path.basename(file)
#             df_list.append(df)
#         except KeyboardInterrupt:
#             raise    
#         except:
#             pass
    
#     return df_list
def get_time_mode(files):
    df_list = []
    for file in files:
        try:
            logstruct = ArduLog(file)
            modes = logstruct.extract_modes()
            assert(len(modes) != 0)
            df = pd.DataFrame(modes, columns = ['TimeMS', 'mode'])
            # df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) 
            df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
            df.name = os.path.basename(file)
            df_list.append(df)
        except KeyboardInterrupt:
            raise    
        except:
            pass
    return df_list

def get_vel(files):
    df_list = []
    for file in files:
        try:
            logstruct = ArduLog(file)
            vel = logstruct.extract_vel()
            assert(len(vel) != 0)
            df = pd.DataFrame(vel, columns = ['TimeMS', 'vn', 've', 'vd'])
            # df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) 
            df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
            df.name = os.path.basename(file)
            df_list.append(df)
        except KeyboardInterrupt:
            raise    
        except:
            pass
    return df_list
def get_type(files):
    type_list = []
    count = 0
    for file in files:
        print(count)
        try:
            logstruct = ArduLog(file)
            flight_type = logstruct.extract_takeoffs()
            type_list.append(flight_type)
        except KeyboardInterrupt:
            raise
        except:
            pass
        count += 1
    return type_list
    # df_list = []
    # for file in files:
    #     try:
    #         vel = ArduLog(file).extract_vel()
    #         df = pd.DataFrame(vel, columns = ['TimeMS', 'vn', 've', 'vd'])
    #         df['TimeMS'] = (df['TimeMS'] - df['TimeMS'].min()) / 1000
    #         df.name = os.path.basename(file)
    #         df_list.append(df)
    #     except KeyboardInterrupt:
    #         raise    
    #     except:
    #         pass
    
    # return df_list
if __name__ == '__main__':

    ############## currency
    # files = get_files()
    # df_time_mode_list = get_time_current(files[:4])
    # count = 1
    # for curr_df in df_time_mode_list:
        
    #     plt.figure(count)
    #     plt.subplot(2,1,1)
    #     plt.plot(curr_df['TimeMS'], curr_df['curr'])
    #     plt.subplot(2,1,2)
    #     plt.plot(curr_df['TimeMS'], curr_df['curr']>=500)
    #     plt.title = ("current_time")
    #     plt.savefig(str(count)+"current_time.png")
    #     count += 1



       # dic = {}
    # curr_res = pd.DataFrame({}, index = dic.keys())
    # for curr_df in df_time_mode_list:
    #     curr_df = curr_df.sort_values(by="TimeMS" , ascending=True)
    #     temp_index = curr_df.index[0]
    #     temp = curr_df.loc[temp_index]['TimeMS']

    #     t = curr_df.loc[:, 'TimeMS']
    #     cur = curr_df.loc[:, 'curr']
    #     for indexs in curr_df.index:
    #         temp1 = curr_df.loc[indexs]['TimeMS']
    #         # t[indexs] = temp1- temp
    #         curr_df.iat[indexs, 0] = temp1 - temp
    #         temp = temp1
    #         # cur[indexs] = cur[indexs]//1
    #         # curr_df.iat[indexs, 0] = cur[indexs]//1
    #         if cur[indexs] < 80:
    #             curr_df.iat[indexs, 1] = 80
    #         if 85 < cur[indexs] <= 1000:
    #             if cur[indexs] - 85 < 1000 - cur[indexs]:
    #                 curr_df.iat[indexs, 1] = 85
    #             else:
    #                 curr_df.iat[indexs, 1] = 1000
    #         # if 85 < cur[indexs] <= 90:
    #         #     curr_df.iat[indexs, 1] = (cur[indexs]//5)*5
    #         # if 90 < cur[indexs] <= 100:
    #         #     curr_df.iat[indexs, 1] = (cur[indexs]//5)*5
    #         # if 100 < cur[indexs] <= 200:
    #         #     curr_df.iat[indexs, 1] = (cur[indexs]//100)*100
    #         # if 200 < cur[indexs] <= 1000:
    #         #     curr_df.iat[indexs, 1] = (cur[indexs]//100)*100
    #         if 1000 < cur[indexs] <= 3000:
    #             curr_df.iat[indexs, 1] = (cur[indexs]//500)*500
    #         if cur[indexs] > 3000:
    #             curr_df.iat[indexs, 1] = 3000
    #     curr_res = curr_res.append(curr_df)
    # grouped = curr_res.groupby(curr_res['curr'])
    # curr_plot = grouped.sum()
    # plt.figure()
    # curr_plot.plot.pie(subplots=True, figsize=(12, 12), title = "currency_time")
    # plt.savefig("currency_time.png")
    # plt.show()
    # pylab.show()

######################modemodemodemodemodemodemodemodemode
    # files = get_files()
    # df_time_mode_list = get_time_mode(files[1:2])
    # dic = {}
    # for mode_df in df_time_mode_list:
    #     plt.figure()
    #     plt.plot(res['TimeMS'], res['cur']>=4)

#     mode_res = pd.DataFrame({}, index = dic.keys())
#     count = 1
#     for mode_df in df_time_mode_list:
#         print(count)
#         count += 1
#         mode_df = mode_df.sort_values(by="TimeMS" , ascending=True)
#         temp_index = mode_df.index[0]
#         temp = mode_df.loc[temp_index]['TimeMS']
#         t = mode_df.loc[:, 'TimeMS']
#         for indexs in mode_df.index:
#             temp1 = mode_df.loc[indexs]['TimeMS']
#             mode_df.iat[indexs, 0]= temp1- temp
#             temp = temp1
# #     grouped=mode_df.groupby(mode_df['mode'])
# #     flight_mode = grouped.sum()
#         mode_res = mode_res.append(mode_df)

#     grouped=mode_res.groupby(mode_res['mode'])
#     flight_mode = grouped.sum()
#     plt.figure()
#     flight_mode.plot(kind = 'bar', title = "mode_time")
#     flight_mode.plot.pie(subplots=True, figsize=(6, 6))
#     plt.savefig("mode_time.png")
# ###################vel vel vel vel vel vel vel vel v = vn + ve
    files = get_files()
    for i in range(148, 171):
        print(i)
        f = files[i:i+1]
        df_curr_list = get_time_current(f)
        df_vel_list = get_vel(f)
        if df_curr_list == [] or df_vel_list == []:
            continue
        df_curr = df_curr_list[0]
        df_curr = df_curr.sort_values(by="TimeMS" , ascending=True)
        df_vel = df_vel_list[0]
        df_vel = df_vel.sort_values(by="TimeMS" , ascending=True)

        #per second
        for indexs in df_curr.index:
            temp = df_curr.loc[indexs]['TimeMS']
            df_curr.iat[indexs, 0]= temp//1
        curr_group = df_curr.groupby(df_curr['TimeMS']).mean()
        
        for indexs in df_vel.index:
            temp = (df_vel.iloc[indexs, 1]**2 + df_vel.iloc[indexs, 2]**2 + df_vel.iloc[indexs, 3]**2)**0.5
            df_vel.iat[indexs, 3] = temp
        for indexs in df_vel.index:
            temp = df_vel.loc[indexs]['TimeMS']
            df_vel.iat[indexs, 0]= temp//1
        vel_group = df_vel.groupby(df_vel['TimeMS']).mean()
        temp = pd.concat([curr_group, vel_group], axis = 1, join = "inner")
        res = pd.DataFrame({'vd':temp['vd'], 'curr':temp['curr']})
        for indexs in res.index:
            if res.loc[indexs]['curr'] < 1000:
                res.drop([indexs], inplace = True)
        
        res = res.sort_values(by="vd" , ascending=True)
        path = "res" + str(i) +".csv"
        res.to_csv(path, index=True, header=True )


    
    # files = get_files()
    # f = files[6:7]
    



    # df_curr_list = get_time_current(f)
    # df_vel_list = get_vel(f)
    # df_curr = df_curr_list[0]
    # df_curr = df_curr.sort_values(by="TimeMS" , ascending=True)
    # df_vel = df_vel_list[0]
    # df_vel = df_vel.sort_values(by="TimeMS" , ascending=True)

    # #per second
    # for indexs in df_curr.index:
    #     temp = df_curr.loc[indexs]['TimeMS']
    #     df_curr.iat[indexs, 0]= temp//1
    # curr_group = df_curr.groupby(df_curr['TimeMS']).mean()
    

    # for indexs in df_vel.index:
    #     temp = (df_vel.iloc[indexs, 1]**2 + df_vel.iloc[indexs, 2]**2 + df_vel.iloc[indexs, 3]**2)**0.5
    #     df_vel.iat[indexs, 3] = temp
    # for indexs in df_vel.index:
    #     temp = df_vel.loc[indexs]['TimeMS']
    #     df_vel.iat[indexs, 0]= temp//1
    # vel_group = df_vel.groupby(df_vel['TimeMS']).mean()
    # temp = pd.concat([curr_group, vel_group], axis = 1, join = "inner")
    # res = pd.DataFrame({'vd':temp['vd'], 'curr':temp['curr']})
    # for indexs in res.index:
    #     if res.loc[indexs]['curr'] < 1000:
    #         res.drop([indexs], inplace = True)
    
    # res = res.sort_values(by="vd" , ascending=True)
    # res.to_csv("res.csv", index=True, header=True )

# type type type type type type type type type type
    # files = get_files()
    # type_list = get_type(files)
    # f = open('data.txt','w')  
    # f.write(str(type_list))
    # f.close() 
    