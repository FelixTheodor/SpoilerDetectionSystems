# TopicModeller is the heart of the similarity calculation 
# between sents from the reviews and topic models that are trained 
# on the book. You need to prepare the book corpus as well as 
# a (sub) goodreads corpus for it to work
# TopicModeller writes 3 output files: sent_sims, signatures and topic_eval
# you can also configure the system to produce context information as well or not

from os import listdir, makedirs
import os
from tqdm import tqdm
import pandas as pd
import numpy as np

from octis.dataset.dataset import Dataset
from octis.models.LDA import LDA
from octis.models.ETM import ETM
from octis.evaluation_metrics.diversity_metrics import TopicDiversity
from octis.evaluation_metrics.similarity_metrics import WordEmbeddingsRBOMatch

from helper.review_struct import Review
from msgspec.json import decode, encode

class TopicModeller:
    def __init__(self, name, algo, n_tpcs, n_parts, metrics, include_context):
        self.name = name
        self.algo = algo
        self.n_tpcs = n_tpcs
        self.n_parts = n_parts
        
        # here it is important that you set the right corpus, 
        # it can be cleaned or uncleaned from noise
        self.gr_path = "gr_corpus/un_sub_corpus.json"
        self.book_path = f"book_corpus/octis/{n_parts}/"
        self.gr_corpus = self.read_gr_corpus(self.gr_path)
        
        self.metrics = metrics
        self.include_context = include_context
    
    def work(self):
        self.all_sdts = pd.DataFrame()
        self.topic_evals = pd.DataFrame()
        self.all_topics = pd.DataFrame()
        
        all_books = listdir(self.book_path)
        
        for book in tqdm(all_books):
            all_tms = []
            #create TM for each part of the book
            for i in range(1,self.n_parts+1):
                d_path = self.book_path+book+"/"+str(i)+"/"
                dataset = Dataset()
                dataset.load_custom_dataset_from_folder(d_path)
                
                if "LDA" in self.algo:
                    nt = self.n_tpcs if i != 0 else 50
                    model = LDA(num_topics=nt)#, embedding_size=200, embeddings_path="word2vec.gz", binary_embeddings="True",embeddings_type="keyedvectors")#LDA(num_topics=num_topics)#CTM(num_topics=num_topics, bert_path=d_path)#  # Create model
                else:
                   model = ETM(num_topics=self.n_tpcs, embedding_size=200, embeddings_path="word2vec/word2vec.gz", binary_embeddings="True",embeddings_type="keyedvectors")#LDA(num_topics=num_topics)#CTM(num_topics=num_topics, bert_path=d_path)#  # Create model 
                
                model_output = model.train_model(dataset) # Train the model
                if (model_output.get("topics")) == None:
                    continue
                word2score = self.get_word2score(model_output, model)
                all_tms.append([word2score,model_output])
                
                topic_scores = [metric.score(model_output) for metric in self.metrics]
                self.topic_evals = pd.concat([self.topic_evals, 
                                             pd.DataFrame({"bookID":book, "part":i, "RBO":topic_scores[0], "Div":topic_scores[1]},index=[0])])
                for j in range(len(word2score)):
                    marklist = sorted(word2score[j].items(), key=lambda x:x[1], reverse=True)[:20]
                    self.all_topics = pd.concat([self.all_topics, 
                                             pd.DataFrame({"bookID":book, "part":i, "topic-id":j,"words":dict(enumerate(marklist))})])
                
                
            bookID = book.split("-")[0]
            
            # create a similarity between each sentence and each topic model estimated before
            sdt = self.get_sent_dist_table(all_tms, bookID)
            self.all_sdts = pd.concat([self.all_sdts, sdt])
        self.save_results()

    def get_word2score(self, output, model):
        allw2s = []
        for i in range(len(output.get("topics"))):
            word_list = model.id2word if hasattr(model, "id2word") else model.vocab
            prob_list = output.get("topic-word-matrix")[i]
            word2score = {}
            for i in range(len(prob_list)):
                word2score[word_list[i]] = prob_list[i]
            allw2s.append(word2score)
        return allw2s
    
    def read_gr_corpus(self, path):
        f = open(path, "rb")
        corpus = []
        for line in f.readlines():
            review = decode(line, type=Review)
            corpus.append(review)
        f.close()
        return corpus
    
    def get_sent_dist_table(self, tms, bookID):
        tms = self.create_vectors(tms)
        
        all_sims = []
        all_ys = []
        all_ids = []
        all_uids = []
        all_sents = []
        all_ppsents = []
        all_partitions = []
        
        all_prevs = []
        all_nexts = []
        
        all_prev_sims = []
        all_next_sims = []
        
        for rev in [rev for rev in self.gr_corpus if rev.book_id == bookID]:
            for i in range(len(rev.preprocessed_sentences)):
                sent = rev.preprocessed_sentences[i]
                o_sent = rev.review_sentences[i]
                next_sent = [None, None]
                prev_sent = [None, None]
                
                sent_sims = []
                prev_sims = []
                next_sims = []
                for j in range(len(tms)):
                    sim = self.get_topic_dist_sim(tms[j], sent[1])
                    sent_sims.append(sim)
                    if self.include_context:
                        if i != 0:
                            prev_sent = rev.preprocessed_sentences[i-1]
                            prev_sim = self.get_topic_dist_sim(tms[j], prev_sent[1])
                            prev_sims.append(prev_sim)
                        else:
                            prev_sims.append(None)
                        if i != len(rev.preprocessed_sentences)-1:
                            next_sent = rev.preprocessed_sentences[i+1]
                            next_sim = self.get_topic_dist_sim(tms[j], next_sent[1])
                            next_sims.append(next_sim)
                        else:
                            next_sims.append(None)

                all_sims.append(sent_sims)
                all_ids.append(rev.book_id)
                all_sents.append(o_sent[1])
                all_ppsents.append(sent[1])
                all_prevs.append(prev_sent[1])
                all_nexts.append(next_sent[1])
                all_ys.append(sent[0])
                all_partitions.append(rev.partition)
                all_uids.append(rev.user_id)
                all_prev_sims.append(prev_sims)
                all_next_sims.append(next_sims)
            
        data = {"bookID":all_ids,"userID":all_uids,"sent":all_sents, "pp_sent":all_ppsents, "partition":all_partitions, 
                "spoiler":all_ys, "next_sent":all_nexts, "prev_sent":all_prevs}
        for i in range(len(all_sims[0])):
            data[i] = []
            for j in range(len(all_sims)):
                data[i].append(all_sims[j][i])
                
        if self.include_context:
            for i in range(len(all_sims[0])):
                data[str(i)+"_next"] = []
                data[str(i)+"_prev"] = []
                for j in range(len(all_sims)):
                    data[str(i)+"_next"].append(all_next_sims[j][i])
                    data[str(i)+"_prev"].append(all_prev_sims[j][i])
                    
        sent_dist_table = pd.DataFrame(data)
        
        return sent_dist_table
    
    def create_vectors(self, tms):
        new_tms = []
        for tm in tms:
            mtr = tm[1]["topic-document-matrix"]
            avg = [np.average(i) for i in mtr]
            new_tms.append([tm[0],avg])
        return new_tms
    
    def get_topic_dist_sim(self, tm, sent):
        if tm[0] == None:
            return 0
        new_sent = [w for w in sent.split() if w in tm[0][0].keys()]
        if len(new_sent) == 0:
            return 0
        
        vec2 = tm[1]
        vec1 = []
        for i in range(len(vec2)):
            td = np.average([tm[0][i][w] for w in new_sent])
            vec1.append(td)
        
        div = (np.linalg.norm(vec1)*np.linalg.norm(vec2))
        if div == 0.0:
            return 0
        cos_sim = np.dot(vec1, vec2)/div
        
        uwp = ((len(sent.split()) - len(new_sent)) / len(sent.split())) * 0.2
        
        return max(0, cos_sim - uwp)
    
    def save_results(self):
        makedirs(f"results/{self.name}/", exist_ok=True)
        self.all_sdts.to_csv(f"results/{self.name}/sent_sims.csv")
        self.topic_evals.to_csv(f"results/{self.name}/topic_eval.csv")
        self.all_topics.to_csv(f"results/{self.name}/topics.csv")