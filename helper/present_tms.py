# this script reads in some result files and produces nice graphs 
# that can be seen in the thesis
# you need to read in your own dfs if you want to see the results
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np


font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)


e_div = 0
e_wbo = 0
c_div = 0
c_wbo = 0
l_div = 0
l_wbo = 0

for i in range(len(df_etm)):
    e_div += df_etm.Div.values[i]
    e_wbo += df_etm.RBO.values[i]
    c_div += df_ctm.Div.values[i] 
    c_wbo += df_ctm.RBO.values[i] 
    l_div += df_lda.Div.values[i]
    l_wbo += df_lda.RBO.values[i] 

print(f"ETM Div: {e_div/len(df_etm)}")
print(f"ETM RBO: {e_wbo/len(df_etm)}")

print(f"CTM Div: {c_div/len(df_etm)}")
print(f"CTM RBO: {c_wbo/len(df_etm)}")

print(f"LDA Div: {l_div/len(df_etm)}")
print(f"LDA RBO: {l_wbo/len(df_etm)}")


barWidth = 0.25
fig = plt.subplots(figsize =(12, 8))
 
# set height of bar
LDA = [l_div/len(df_etm), l_wbo/len(df_etm), l_div/len(df_etm) * l_wbo/len(df_etm)]
ETM = [e_div/len(df_etm), e_wbo/len(df_etm), e_div/len(df_etm) * e_wbo/len(df_etm)]
CTM = [c_div/len(df_etm), c_wbo/len(df_etm), c_div/len(df_etm) * c_wbo/len(df_etm)]
 
# Set position of bar on X axis
br1 = np.arange(3)
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]
 
# Make the plot
plt.bar(br1, LDA, color ='r', width = barWidth,
        edgecolor ='grey', label ='LDA')
plt.bar(br2, ETM, color ='g', width = barWidth,
        edgecolor ='grey', label ='ETM')
plt.bar(br3, CTM, color ='b', width = barWidth,
        edgecolor ='grey', label ='CTM')
 
# Adding Xticks
plt.xticks([r + barWidth for r in range(len(LDA))],
        ["Topic Diversity", "WERBO-M", "Combined"])
 
plt.legend()
plt.show()

fig, ax = plt.subplots()
rects1 = ax.bar("Topic Diversity", [l_div/len(df_etm),e_div/len(df_etm)], label="LDA")
rects2 = ax.bar("WERBO-M", l_wbo/len(df_etm), label="LDA")
#rects1 = ax.bar("Topic Diversity", , label="ETM")
#rects2 = ax.bar("WERBO-M", e_wbo/len(df_etm), label="ETM")
#plt.title(book.split("-")[0])
plt.legend()
plt.show()