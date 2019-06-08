import numpy as np
import pandas as pd
import calmap
import matplotlib.pyplot as plt
import hvplot
import hvplot.pandas
import holoviews as hv



df = pd.read_pickle('data/dates.pkl')
# df = df[['Flight Date','Flight Durations']]
# df = df[~df['Flight Date'].isnull()]
# df = df.groupby('Flight Date').agg(sum)
# df['Flight Durations'] = df['Flight Durations'].apply(lambda x: sorted(x))

# for i in range(0,len(df['Flight Durations'])):
#     old_list = df['Flight Durations'][i]
#     new_list = [x for x in old_list if x>20]
#     df['Flight Durations'][i] = new_list

# flights = df['Flight Durations'].apply(pd.Series)
# flights = flights.rename(columns = lambda x : 'Flight ' + str(x))

# #%opts Bars [tools=['hover'],legend_position='left',color_index='Variable',width=900,height=400](alpha=0.5,color=hv.Palette('Category20'))
# flights.hvplot.bar(stacked=True,rot=45).redim(value=hv.Dimension('value',label='Duration')).relabel('Duration')


#flights.hvplot.bar(stacked=True)
