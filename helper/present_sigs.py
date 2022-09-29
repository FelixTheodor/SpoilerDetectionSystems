# this script reads in some result files and produces nice graphs 
# that can be seen in the thesis
import pandas as pd
import matplotlib 
from matplotlib import pyplot as plt
from ast import literal_eval
import numpy as np

df = pd.read_csv("results/LDAVisual-200_10_sigs.csv")
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)
def older():


    sigs = {}
    for _, row in df.iterrows():
        if row.bookID in sigs.keys():
            sigs[row.bookID][0].append(row.spoiler)
            sigs[row.bookID][1].append(row.nonspoiler)
        else:
            sigs[row.bookID] = [[row.spoiler], [row.nonspoiler]]

    x = np.arange(200)
    width = 0.35

    for book in sigs.keys():
        sp = sigs[book][0]
        gn = sigs[book][1]
        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, gn, label="general similarity")
        rects2 = ax.bar(x + width / 2, sp, label="spoiler similarity")
        plt.title(book.split("-")[0])
        plt.legend()
        plt.show()
        #plt.plot(range(len(gn)), gn, label="general similarity")
        #plt.plot(range(len(sp)), sp, label="spoiler similarity")
        #plt.title(book)
        #plt.legend()
    #plt.title("All Spoiler Similarities")
        #plt.show()

def old():
    print(df.columns.values)
    print(df.iloc[0].bookID)
    print(literal_eval(df.iloc[0].general_sim_avg))
    all_sp = [0 for i in range(10)]
    #plt.plot(range(1,11), literal_eval(df.iloc[0].general_sim_avg))
    for _, row in df.iterrows():
        gn = literal_eval(row.general_sim_avg)
        sp = literal_eval(row.general_sp_signature)
        sp = [gn[i] + sp[i] for i in range(10)]
        plt.plot(range(1,11), gn, label="general similarity")
        plt.plot(range(1,11), sp, label="spoiler similarity")
        plt.title(row.bookID)
        plt.legend()
        plt.show()

    all_cl = literal_eval(df.iloc[0].cluster_sp_signatures)
    for cl in all_cl:
        plt.plot(range(1,11), cl)
older()