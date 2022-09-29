# Presenter reads the results of former steps
# and does some evaluation on them - not necessary any longer,
# since evaluation is now done through TABLEARN
# might still be useful to do some local evaluation
import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

class Presenter:
    def __init__(self, name):
        self.name = name
        self.path = f"results/{self.name}/"
    
    def present(self):
        df_scores = pd.read_csv(self.path+"scores.csv")
        df_evals = pd.read_csv(self.path+"topic_eval.csv")
        val_corpus = df_scores[(df_scores["partitition"] == "VAL")]
        train_corpus = df_scores[(df_scores["partitition"] == "TRN")]
        
        ys = []
        gn_scores = []
        cl_scores = []
        
        for _, row in val_corpus.iterrows():
            bid = row["bookID"]
            ys.append(row["spoiler"])

            gn_scores.append(row["gn_spind"])
            
            cl_scores.append(np.average([1 - row["cl_nsind"],row["cl_spind"]]))
            
        
        ys2 = ys
        gn_preds = self.score_to_pred(gn_scores)
        cl_preds = self.score_to_pred(cl_scores)
        
        ys, gn_preds, gn_scores = self.outweigh(ys, gn_preds, gn_scores)
        _, cl_preds, cl_scores = self.outweigh(ys2, cl_preds, cl_scores)
        
        gn_roc, gn_prec, gn_rec, gn_f1 = self.compute_results(ys, gn_preds, gn_scores)
        cl_roc, cl_prec, cl_rec, cl_f1 = self.compute_results(ys, cl_preds, cl_scores)
        
        rbo = []
        div = []
        for _,row in df_evals.iterrows():
            rbo.append(row["RBO"])
            div.append(row["Div"])
        gte = 2 * ((np.average(rbo) * np.average(div))/(np.average(rbo)+ np.average(div)))
            
        
        print(f"{self.name}.gn\t\t{gn_roc*100}\t{gn_prec*100}\t{gn_rec *100}\t{gn_f1*100}\t{gte*100}")
        print(f"{self.name}.cl\t\t{cl_roc*100}\t{cl_prec*100}\t{cl_rec *100}\t{cl_f1*100}\t{gte*100}")
        
    
    def compute_results(self, ys, preds, scores):
        roc = roc_auc_score(ys, scores)
        prec = precision_score(ys, preds)
        rec = recall_score(ys, preds)
        f1 = f1_score(ys, preds)
        
        return roc, prec, rec, f1
    
    def combine_bl_scores(self, pos, ubs, bbs):
        all_scores = []
        for i in range(len(pos)):
            nscore = np.average([pos[i],ubs[i],bbs[i]])
            all_scores.append(nscore)
        return all_scores
    
    def score_to_pred(self, scores):
        preds = []
        if len(scores) == 0:
            return preds
        sorted_list = sorted(scores, reverse=True)
        max_val = sorted_list[int(len(scores) * 0.5)]
        
        #avg = np.average(scores)
        for score in scores:
            if score >= max_val:# and score > 0:
                preds.append(1)
            else:
                preds.append(0)
        return preds
    
    def outweigh(self, trues, preds, scores):
        x = len([i for i in trues if i==1])
        y = len([i for i in trues if i==0])
        factor = y/x if x!= 0 else 0
        new_trues = []
        new_preds = []
        new_scores = []
        for i in range(len(preds)):
            if trues[i] == 0:
                new_trues.append(0)
                new_preds.append(preds[i])
                new_scores.append(scores[i])
            else:
                for _ in range(int(factor)):
                    new_trues.append(1)
                    new_preds.append(preds[i])
                    new_scores.append(scores[i])
        x = len([i for i in new_trues if i==1])
        y = len([i for i in new_trues if i==0])
        return new_trues, new_preds, new_scores