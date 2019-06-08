import numpy as np
import pandas as pd
import calmap
import matplotlib.pyplot as plt
import hvplot
import hvplot.pandas
import holoviews as hv
import math


df = pd.read_pickle('data/dates.pkl')
df = df[['Flight Date','Flight Durations']]
df = df[~df['Flight Date'].isnull()]
df = df.groupby('Flight Date').agg(sum)
df['Flight Durations'] = df['Flight Durations'].apply(lambda x: sorted(x))

list_of_all_durations = []
for i in range(0,len(df['Flight Durations'])):
    old_list = df['Flight Durations'][i]
    new_list = [x for x in old_list if x>20]
    list_of_all_durations.extend(new_list)

bins = np.linspace(math.ceil(min(list_of_all_durations)),math.floor(max(list_of_all_durations)),20) # fixed number of bins
plt.xlim([min(list_of_all_durations)-5, max(list_of_all_durations)+5])

plt.hist(list_of_all_durations, bins=bins, alpha=0.5, rwidth=0.95)
plt.grid(axis='y', alpha=0.5)
plt.title('Time of Flight')
plt.text(550, 22, r'$\mu = 230 s, \sigma = 185 s$')
plt.xlabel('Time(s)')
plt.ylabel('count')

plt.show()