# main method for LDA1 and LDA10, both can be configured and run from here

from LDA10.TopicModeller import TopicModeller
from LDA10.Trainer import Trainer
from LDA10.Validator import Validator
from LDA10.Presenter import Presenter
from LDA1.LDA1 import LDA1

from octis.evaluation_metrics.diversity_metrics import TopicDiversity
from octis.evaluation_metrics.similarity_metrics import WordEmbeddingsRBOMatch

# set all configs that should be run
# first number is number of topics, sencond is number of parts (only relevant for lda10, 10 is used in MA)
all_configs = ["LDA-20_10"]

#initialize metrics, WERBO needs a pretrained word2vec vector file
metrics = [WordEmbeddingsRBOMatch(word2vec_path="word2vec/word2vec_books_only.wv",topk=10, binary=False), TopicDiversity(topk=10)]

for conf in all_configs:
    print(f"###############################################################################")
    print(f"#################################  {conf}  #################################")
    print(f"###############################################################################")
    
    base = conf.split("-")[0]
    tpc_n = int(conf.split("-")[1].split("_")[0])
    parts = int(conf.split("_")[1])
    
    # uncomment the steps you want to do
    
    # uncomment this to do LDA1
    #lda1 = LDA1(conf, base, tpc_n, parts, None, True)
    #lda1.work()
    
    
    # uncomment this to do LDA10
    #tm = TopicModeller(conf, base, tpc_n, parts, metrics, True)
    #tm.work()
    
    tr = Trainer(conf)
    tr.work()
    
    va = Validator(conf, True)
    va.work()
    
    
    print("METHOD\t\t\tROC\t\t\tPREC\t\t\tREC\t\t\tF1\t\t\tTE")
    
    pr = Presenter(conf)
    pr.present()