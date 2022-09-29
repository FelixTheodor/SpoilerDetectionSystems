# the validator does the actual calculation of the scores
# it takes the sent_sim output of the TopicModeller as well as the 
# signatures output of the Trainer and finds for each sentence in 
# the review corpus the most similar cluster. 

from tqdm import tqdm
from ast import literal_eval
import pandas as pd
import numpy as np
from msgspec.json import decode
from helper.review_struct import Review

class Validator:
    def __init__(self, name, include_context):
        self.name = name
        self.path = f"results/{self.name}/"
        self.include_context = include_context
    
    def work(self):
        df_sents = pd.read_csv(f"{self.path}sent_sims.csv")
        df_sigs = pd.read_csv(f"{self.path}signatures.csv")
        
        #ub = self.get_bias(df_sents)
        ub = dict()
        
        gn_sp_book2sig, gn_avg_book2sig, cl_sp_book2sig, cl_ns_book2sig = self.get_book2sigs(df_sigs)
        
        all_ids = []
        all_ub = []
        all_bb =[]
        all_sents = []
        all_partitions = []
        all_spoilerys = []
        
        all_gn_sp_ind = []
        all_cl_sp_ind = []
        all_cl_ns_ind = []
        all_gn_sp_ind_next = []
        all_cl_sp_ind_next = []
        all_cl_ns_ind_next = []
        all_gn_sp_ind_prev = []
        all_cl_sp_ind_prev = []
        all_cl_ns_ind_prev = []
        
        for _, row in tqdm(df_sents.iterrows()):
            scores = [row[str(i)] for i in range(10)]
            bookID = row['bookID']
            
            gn_spoiler_ind = self.get_gn_spoiler_ind(scores, gn_sp_book2sig[bookID], gn_avg_book2sig[bookID])
            cl_spoiler_ind, cl_nonsp_ind = self.get_cl_spoiler_ind(scores, cl_sp_book2sig[bookID], cl_ns_book2sig[bookID], gn_avg_book2sig[bookID])
            
            if self.include_context:
                scores_prev = [row[str(i)+"_prev"] for i in range(10)]
                scores_next = [row[str(i)+"_next"] for i in range(10)]
                gn_spoiler_ind_prev = self.get_gn_spoiler_ind(scores_prev, gn_sp_book2sig[bookID], gn_avg_book2sig[bookID])
                cl_spoiler_ind_prev, cl_nonsp_ind_prev = self.get_cl_spoiler_ind(scores_prev, cl_sp_book2sig[bookID], cl_ns_book2sig[bookID], gn_avg_book2sig[bookID])
                gn_spoiler_ind_next = self.get_gn_spoiler_ind(scores_next, gn_sp_book2sig[bookID], gn_avg_book2sig[bookID])
                cl_spoiler_ind_next, cl_nonsp_ind_next = self.get_cl_spoiler_ind(scores_next, cl_sp_book2sig[bookID], cl_ns_book2sig[bookID], gn_avg_book2sig[bookID])
            
            
            all_ids.append(bookID)
            all_sents.append(row['sent'].replace(",", ""))
            all_partitions.append(row['partition'])
            all_spoilerys.append(row['spoiler'])
            all_gn_sp_ind.append(gn_spoiler_ind)
            all_cl_sp_ind.append(cl_spoiler_ind)
            all_cl_ns_ind.append(cl_nonsp_ind)
            all_cl_ns_ind_prev.append(cl_nonsp_ind_prev)
            all_cl_sp_ind_prev.append(cl_spoiler_ind_prev)
            all_gn_sp_ind_prev.append(gn_spoiler_ind_prev)
            all_cl_ns_ind_next.append(cl_nonsp_ind_next)
            all_cl_sp_ind_next.append(cl_spoiler_ind_next)
            all_gn_sp_ind_next.append(gn_spoiler_ind_next)
                
            if row["userID"] in ub.keys():
                all_ub.append(ub[row["userID"]])
            else:
                all_ub.append(0)
            #all_bb.append(bb[bookID])
        
        self.all_inds = pd.DataFrame({"bookID":all_ids, "sent":all_sents, "partitition":all_partitions,
                                      "spoiler":all_spoilerys, "gn_spind":all_gn_sp_ind,
                                      "cl_spind":all_cl_sp_ind, "cl_nsind":all_cl_ns_ind,
                                      "user_bias":all_ub })#"book_bias":all_bb})
        if self.include_context:
            self.all_inds["gn_spind_next"] = all_gn_sp_ind_next
            self.all_inds["cl_spind_next"] = all_cl_sp_ind_next
            self.all_inds["cl_nsind_next"] = all_cl_ns_ind_next
            self.all_inds["gn_spind_prev"] = all_gn_sp_ind_prev
            self.all_inds["cl_spind_prev"] = all_cl_sp_ind_prev
            self.all_inds["cl_nsind_prev"] = all_cl_ns_ind_prev
            
        
        self.save_results()
            
    
    def get_book2sigs(self, df):
        gn_sp_book2sig = {}
        gn_book2sig = {}
        cl_sp_book2sig = {}
        cl_ns_book2sig = {}
        
        
        for _, row in df.iterrows():
            gn_sp_book2sig[row['bookID']] = literal_eval(row['general_sp_signature'])
            gn_book2sig[row['bookID']] = literal_eval(row['general_sim_avg'])
            cl_sp_book2sig[row['bookID']] = literal_eval(row['cluster_sp_signatures'])
            cl_ns_book2sig[row['bookID']] = literal_eval(row['cluster_ns_signatures'])
        
        return gn_sp_book2sig, gn_book2sig, cl_sp_book2sig, cl_ns_book2sig
    
    def get_gn_spoiler_ind(self, scores, sp_sig, gn_sig):
        diff_scores = [scores[i] - gn_sig[i] for i in range(len(scores))]
        div = (np.linalg.norm(diff_scores)*np.linalg.norm(sp_sig))
        if div == 0.0:
            return 0
    
        return np.dot(diff_scores, sp_sig)/div

    def get_cl_spoiler_ind(self, scores, spoiler_sigs, nonsp_sigs, gn_sig):
        diff_scores = [scores[i] - gn_sig[i] for i in range(len(scores))]
        
        spoiler_score = self.get_max_sim(diff_scores, spoiler_sigs)
        nonsp_score = self.get_max_sim(diff_scores, nonsp_sigs)
        
        return spoiler_score, nonsp_score
    
    def get_max_sim(self, scores, sigs):
        max_sim = 0
        for sig in sigs: 
            div = np.linalg.norm(sig)*np.linalg.norm(scores)
            sim = 0 if div == 0.0 else np.dot(sig, scores)/div
            max_sim = sim if sim > max_sim else max_sim
        return max_sim
    
    def get_bias(self, corpus):
        blacklist = set()
        whitelist = set()
        for _,row in corpus.iterrows():
            blacklist.add(row["sent"])
            whitelist.add(row["userID"])
        f = open("gr_corpus/gr_all.json", "rb")
        corpus = []
        for line in f.readlines():
            review = decode(line, type=Review)
            if review.user_id in whitelist:
                corpus.append(review)
        f.close()
        
        count = 0
        
        u2b = {}
        for rev in tqdm(corpus):
            uid = rev.user_id
            for sent in rev.review_sentences:
                if sent[1] not in blacklist:
                    if uid in u2b.keys():
                        u2b[uid].append(sent[0])
                    else:
                        u2b[uid] = [sent[0]]
                else:
                    count += 1
        for k in u2b.keys():
            val = np.sum(u2b[k]) / len(u2b[k])
            u2b[k] = val
        print(count)
        return u2b
        
    
    def save_results(self):
        self.all_inds.to_csv(self.path+"scores.csv")