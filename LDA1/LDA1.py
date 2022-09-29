# LDA1 works holds all the code for the LDA1 system
# in contrast to LDA10, there are no in between steps stored
# it just produces three output files in the results folder: 
# signatures, topics and scores of all the sentences

from LDA10.TopicModeller import TopicModeller
import pickle
from math import isnan
import numpy as np
import pandas as pd
from os import listdir
from octis.dataset.dataset import Dataset
from octis.models.LDA import LDA
from octis.models.ETM import ETM
from scipy import spatial
from tqdm import tqdm

class LDA1:
    def __init__(self, name, algo, n_tpcs, n_parts, metrics, include_context):
        self.name = name
        self.algo = algo
        self.n_tpcs = n_tpcs
        self.n_parts = n_parts
        self.book_path = f"book_corpus/octis/{n_parts}/"
        self.include_context = include_context
        
        self.tm = TopicModeller(name, algo, n_tpcs, n_parts, metrics, include_context)
        self.idfs = pickle.load(open("helper/idfs.pickle", "rb"))
    
    def work(self):
        all_books = listdir(self.book_path)
        self.all_topics = pd.DataFrame()
        self.all_sigs = pd.DataFrame()
        all_sims = []
        all_sims_prev = []
        all_sims_next = []
        all_sps = []
        all_tfids = []
        all_sents = []
        all_bids = []
        
        for book in all_books:
            d_path = self.book_path+book+"/0/"
            dataset = Dataset()
            dataset.load_custom_dataset_from_folder(d_path)
                
            if "LDA" in self.algo:
                nt = self.n_tpcs# if i != 0 else 50
                model = LDA(num_topics=nt)#, embedding_size=200, embeddings_path="word2vec.gz", binary_embeddings="True",embeddings_type="keyedvectors")#LDA(num_topics=num_topics)#CTM(num_topics=num_topics, bert_path=d_path)#  # Create model
            else:
                model = ETM(num_topics=self.n_tpcs, embedding_size=200, embeddings_path="word2vec/word2vec.gz", binary_embeddings="True",embeddings_type="keyedvectors")#LDA(num_topics=num_topics)#CTM(num_topics=num_topics, bert_path=d_path)#  # Create model 
            
            model_output = model.train_model(dataset) # Train the model
            if (model_output.get("topics")) == None:
                continue
            word2score = self.tm.get_word2score(model_output, model)
                
            bookID = book.split("-")[0]
            
            ns = [[] for i in range(len(word2score))]
            sp = [[] for i in range(len(word2score))]
            
            # walk trough all training instances and estimate average spoiler / non spoiler sims
            for rev in [rev for rev in self.tm.gr_corpus if rev.book_id == bookID and rev.partition == "TRN"]:
                sents = rev.preprocessed_sentences
                current_spec = self.compute_specificity(sents)
                for i in range(len(rev.preprocessed_sentences)):
                    sent = rev.preprocessed_sentences[i]
                    o_sent = rev.review_sentences[i]
                    
                    sent_sims = []
                    for i in range(len(word2score)):
                        sim = self.topic_sim(word2score[i], sent[1], current_spec)
                        sent_sims.append(sim)
                    sim_sum = np.sum(sent_sims) + 0.00000000000000001
                    sent_sims = [(i / sim_sum if not isnan(i) else 0) for i in sent_sims]
                    if sent[0] == 1:
                        for i in range(len(sent_sims)):
                            sp[i].append(sent_sims[i] if not isnan(sent_sims[i]) else 0)
                    if sent[0] == 0:
                        for i in range(len(sent_sims)):
                            ns[i].append(sent_sims[i] if not isnan(sent_sims[i]) else 0)
            sp = [np.average([i for i in el if i > 0]) for el in sp]
            ns = [np.average([i for i in el if i > 0]) for el in ns]
            self.all_sigs = pd.concat([self.all_sigs, 
                                             pd.DataFrame({"bookID":book, "spoiler":sp, "nonspoiler":ns})])
            print(f"\n{book}\n{1 - spatial.distance.cosine(sp, ns)}\n")
            sp = [sp[i] - ns[i] for i in range(len(sp))]
            
            for j in range(len(word2score)):
                marklist = sorted(word2score[j].items(), key=lambda x:x[1], reverse=True)[:20]
                self.all_topics = pd.concat([self.all_topics, 
                                             pd.DataFrame({"bookID":book, "topic-id":j,"words":dict(enumerate(marklist))})])
            
            #continue
            for rev in tqdm([rev for rev in self.tm.gr_corpus if rev.book_id == bookID]):
                sents = rev.preprocessed_sentences
                current_spec = self.compute_specificity(sents)
                for i in range(len(rev.preprocessed_sentences)):
                    sent = rev.preprocessed_sentences[i]
                    o_sent = rev.review_sentences[i]
                    
                    sent_sims = []
                    next_sims = []
                    prev_sims = []
                    
                    for j in range(len(word2score)):
                        sim = self.topic_sim(word2score[j], sent[1], current_spec)
                        sent_sims.append(sim)
                        if self.include_context:
                            if i != 0:
                                prev_sent = rev.preprocessed_sentences[i-1]
                                prev_sim = self.topic_sim(word2score[j], prev_sent[1], current_spec)
                                prev_sims.append(prev_sim)
                            
                            if i != len(rev.preprocessed_sentences)-1:
                                next_sent = rev.preprocessed_sentences[i+1]
                                next_sim = self.topic_sim(word2score[j], next_sent[1],current_spec)
                                next_sims.append(next_sim)
                            
                    sim_sum = np.sum(sent_sims) + 0.00000000000000001
                    sent_sims = [(i / sim_sum if not isnan(i) else 0) for i in sent_sims]
                    sent_sims = [sent_sims[i] - ns[i] for i in range(len(sent_sims))]
                    
                    if len(next_sims) != 0:
                        next_sum = np.sum(next_sims) + 0.00000000000000001
                        next_sims = [(i / next_sum if not isnan(i) else 0) for i in next_sims]
                        next_sims = [next_sims[i] - ns[i] for i in range(len(next_sims))]
                    
                    if len(prev_sims) != 0:
                        prev_sum = np.sum(prev_sims) + 0.00000000000000001
                        prev_sims = [(i / prev_sum if not isnan(i) else 0) for i in prev_sims]
                        prev_sims = [prev_sims[i] - ns[i] for i in range(len(prev_sims))]
                    
                    all_sims.append(1 - spatial.distance.cosine(sp, sent_sims))
                    if len(prev_sims) != 0:
                        all_sims_prev.append(1 - spatial.distance.cosine(sp, prev_sims))
                    else:
                        all_sims_prev.append(None)
                    if len(next_sims) != 0:
                        all_sims_next.append(1 - spatial.distance.cosine(sp, next_sims))
                    else:
                        all_sims_next.append(None)
                    
                    all_tfids.append(np.average([current_spec[w] for w in sent[1].split()]))
                    all_sps.append(sent[0])
                    all_sents.append(o_sent[1])
                    all_bids.append(book)
            print(len(all_sims))
            print(len(all_sims_prev))
            print(len(all_sims_next))
                    
        data = {"bookID":all_bids, "sent":all_sents, "sim":all_sims, "spoiler":all_sps, "tfidf":all_tfids}
        if self.include_context:
            data["sim_prev"] = all_sims_prev
            data["sim_next"] = all_sims_next
        self.save_results(pd.DataFrame(data))
        
    def save_results(self, df):
        df.to_csv(f"results/{self.name}.csv")
        self.all_topics.to_csv(f"results/{self.name}_topics.csv")
        self.all_sigs.to_csv(f"results/{self.name}_sigs.csv")
    
    def topic_sim(self, topic, sent, spec):
        new_sent = [w for w in sent.split() if (w in topic.keys())]
        if len(new_sent) == 0:
            return 0
        return np.average([topic[w] * spec[w] for w in new_sent])
            
    
    def compute_specificity(self, sents):
        all_words = {}
        w_count = 0
        for sent in sents:
            for w in sent[1].split():
                w_count += 1
                if w in all_words.keys():
                    all_words[w] += 1
                else:
                    all_words[w] = 1
        
        for w in all_words.keys():
            spec = (all_words[w]/w_count) * self.idfs[w]
            all_words[w] = spec
        return all_words