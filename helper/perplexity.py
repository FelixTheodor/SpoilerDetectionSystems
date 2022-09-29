# this script calculates the perplexity of all the words in a given csv file 
# and dumps it in a pickle file
import pandas as pd
import math
import pickle

df = pd.read_csv("results/LDA-10_10/sent_sims.csv")

idfs = {}
dc = 0
for sent in df["pp_sent"].values:
    if isinstance(sent, float):
        continue
    dc += 1
    s = set(sent.split())
    for el in s:
        if el in idfs.keys():
            idfs[el] += 1
        else:
            idfs[el] = 1

for k in idfs.keys():
    idfs[k] = math.log(float(dc)/ idfs[k])

print(len(idfs.keys()))
print(dc)

pickle.dump(idfs, open("helper/idfs.pickle", "wb"))
