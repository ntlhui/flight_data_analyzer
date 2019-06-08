import numpy as np
import pandas as pd
import calmap
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/altitudes.csv')

#df = df['Alt']
bins = [0,25,50,75,100,150,200,250,300]
df['binned'] = pd.cut(df['Alt'], bins)
s = df.groupby(pd.cut(df['Alt'], bins=bins)).size()
df = pd.DataFrame({"Time Spent (s)": s.values},
                  index=s.index)
ax = sns.heatmap(df, fmt="g", cmap='viridis')
ax.set( ylabel='Altitude Brackets (m)')
ax.invert_yaxis()
plt.show()