import numpy as np
import pandas as pd
import calmap
import matplotlib.pyplot as plt

df = pd.read_pickle('data/dates.pkl')
df = df[['Flight Date','Number of Flights','Flight Durations']]
#df = df[['Flight Date','Number of Flights']]
df = df[~df['Flight Date'].isnull()]
df = df.groupby(['Flight Date']).agg(sum) 

for i in range(0,len(df['Flight Durations'])):
    old_list = df['Flight Durations'][i]
    new_list = [x for x in old_list if x>20]
    df['Flight Durations'][i] = new_list
    df['Number of Flights'][i] = len(new_list)

df['Number of Flights'] = np.log(df['Number of Flights'])
#df = df.reindex(df.index.repeat(df['Number of Flights']))
s = df.ix[:,0]
s.index = pd.to_datetime(s.index)
# fig, ax = calmap.calendarplot(s)
# plt.show()

fig,ax = calmap.calendarplot(s,fig_kws=dict(figsize=(17,8)))

fig.colorbar(ax[0].get_children()[1], ax=ax.ravel().tolist())
plt.show()