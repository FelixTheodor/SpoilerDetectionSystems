# main file to create the baseline information for the corpus

import pandas as pd
import numpy as np
import pickle
from system.Presenter import Presenter

def get_bbs(corpus):
    try:
        return pickle.load(open("b2b.pickle", "rb"))
    except:
        b2b = {}
        for _,row in corpus.iterrows():
            if row["partitition"] != "TRN":
                continue
            bid = row["bookID"]
            if bid in b2b.keys():
                b2b[bid].append(row["spoiler"])
            else:
                b2b[bid] = [row["spoiler"]]  
        for k in b2b.keys():
            val = np.sum(b2b[k]) / len(b2b[k])
            b2b[k] = val
        pickle.dump(b2b, open("b2b.pickle", "wb"))
        return b2b

df_sents = pd.read_csv(f"results/LDA-10_10/sent_sims.csv")
df_scores = pd.read_csv(f"results/LDA-10_10/scores.csv")
ubs = get_bbs(df_scores)

all_pos = []
all_ubs = []
all_bbs = []
all_sp = []

lastID = ""
count = 0
ignore = []
for _,row in df_sents.iterrows():
    currentID = str(row["bookID"])+str(row["userID"])
    if currentID == lastID:
        count += 1
    else:
        for i in range(1, count+1):
            all_pos.append(i/count)
        count = 1
        lastID = currentID
    all_bbs.append(ubs[row["bookID"]])
for i in range(1, count+1):
    all_pos.append(i/count)

for _,row in df_scores.iterrows():
    ub = row["user_bias"]
    sp = row["spoiler"]
    all_ubs.append(ub)
    all_sp.append(sp)
assert len(all_bbs) == len(all_ubs) == len(all_pos) == len(all_sp)

new_df = pd.DataFrame({"book_bias":all_bbs, "position":all_pos})
new_df = df_scores.join(new_df)
new_df.to_csv("all_scores.csv", index=False)


pr = Presenter("baseline")
all_scores = pr.combine_bl_scores(all_pos, all_ubs, all_bbs)
all_preds = pr.score_to_pred(all_scores)
all_sp, all_preds, all_scores = pr.outweigh(all_sp, all_preds, all_scores)
roc, prec, rec, f1 = pr.compute_results(all_sp, all_preds, all_scores)

print("METHOD\t\t\tROC\t\t\tPREC\t\t\tREC\t\t\tF1")
print(f"Baseline\t\t{roc*100}\t{prec*100}\t{rec *100}\t{f1*100}")