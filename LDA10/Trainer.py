# The trainer reads the output from the TopicModeller and performs 
# the training step of the system: clustering spoiler and non spoiler 
# sentences and create an average similarity vector for each cluster
# this average vector is then stored in a csv file as a signature

import pandas as pd
import numpy as np
from ast import literal_eval
from tqdm import tqdm

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import OPTICS 
from sklearn.metrics.pairwise import cosine_similarity

class Trainer:
    def __init__(self, name):
        self.name = name
        self.path = f"results/{self.name}/"
    
    def work(self):
        df = pd.read_csv(f"{self.path}sent_sims.csv")
        
        self.all_sigs = pd.DataFrame()
        
        for book in tqdm(list(set(df['bookID'].to_list()))):
            ns_corpus = df[(df["bookID"] == book) & (df["spoiler"] == 0) & (df["partition"] == "TRN")]
            sp_corpus = df[(df["bookID"] == book) & (df["spoiler"] == 1) & (df["partition"] == "TRN")]
            
            gn_sim_by_part = self.create_sim_by_part(ns_corpus)
            gn_sim_avg = [np.average(i) for i in gn_sim_by_part]
            
            sp_sim_by_part = self.create_sim_by_part(sp_corpus)
            sp_sim_avg = [np.average(i) for i in sp_sim_by_part]
            gn_sp_sig = [sp_sim_avg[i] - gn_sim_avg[i] for i in range(len(gn_sim_avg))]
            
            cl_ns_sig = self.get_clustered_sigs(ns_corpus, gn_sim_by_part, gn_sim_avg)
            cl_sp_sig = self.get_clustered_sigs(sp_corpus, sp_sim_by_part, gn_sim_avg)
            
            cl_ns_sig = self.eliminate_noisy_ns_cluster(cl_ns_sig, cl_sp_sig)
            
            self.all_sigs = pd.concat(
            [pd.DataFrame(index=[0], 
                          data={"bookID":book, "len_ns_input":len(ns_corpus), 
                        "len_sp_input":len(sp_corpus),"general_sp_signature": str(gn_sp_sig), 
                        "general_sim_avg":str(gn_sim_avg),
                        "cluster_sp_signatures":str(cl_sp_sig), "cluster_ns_signatures":str(cl_ns_sig)
                            }), 
            self.all_sigs])
        self.save_results()
        
    def create_sim_by_part(self, corpus):
        sim_lists = []
        for i in range(0, 10):
            sims = corpus[str(i)]
            sim_lists.append(sims.values)
        return sim_lists
    
    def get_clustered_sigs(self, corpus, sim_by_part, avg_sim):
        normalized_sp = []
        for j in range(len(sim_by_part[0])):
            sp_entry = []
            for i in range(len(avg_sim)):
                sp_entry.append(sim_by_part[i][j] - avg_sim[i])
            normalized_sp.append(sp_entry)
        X = StandardScaler().fit_transform(normalized_sp)

        op = OPTICS(min_samples=2).fit(X)
        labels = op.labels_

        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise_ = list(labels).count(-1)
        
        all_cluster_avgs = []
        for j in range(n_clusters_):
            numbers = [normalized_sp[i] for i in range(len(labels)) if labels[i] == j]
            all_cluster_avgs.append([np.average([numbers[i][j] for i in range(len(numbers))]) for j in range(len(numbers[0]))])
        
        return all_cluster_avgs
    
    def eliminate_noisy_ns_cluster(self, nonspoiler, spoiler):
        new_ns = []
        for cl_ns in nonspoiler:
            max_sim = 0
            for cl_sp in spoiler:
                div = np.linalg.norm(cl_ns)*np.linalg.norm(cl_sp)
                sim = 0 if div == 0.0 else np.dot(cl_ns, cl_sp)/div
                max_sim = sim if sim > max_sim else max_sim
            if 0.5 > max_sim:
                new_ns.append(cl_ns)
        return new_ns
                    
    
    def save_results(self):
        self.all_sigs.to_csv(self.path+"signatures.csv")