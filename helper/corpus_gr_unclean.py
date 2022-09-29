# this scirpt creates a small csv file that just contains the vanilla 
# spoiler annotations of the goodreads sub corpus
from msgspec.json import decode, encode
from review_struct import Review
import pandas as pd
from os import listdir

def load_corpus(path, ids):
    f = open(path, "rb")
    corpus = []
    for line in f.readlines():
        review = decode(line, type=Review)
        if review.book_id in ids:
            corpus.append(review)
    f.close()
    return corpus

def get_ids():
    all_relevant_ids = []
    with open("book_corpus/meta/final_book_ids1.txt", "r") as f:
        for line in f.readlines():
            if "-" in line:
                all_relevant_ids.append(line.split("-")[0])
            if "." in line:
                all_relevant_ids.append(line.split(".")[0])
    return all_relevant_ids

rev_ids = get_ids()
ids = listdir(f"book_corpus/octis/10/")
corpus = load_corpus("gr_corpus/gr_all.json", rev_ids)

sp = []

for i in ids:
    i = i.split("-")[0]
    for rev in corpus:
        if rev.book_id != i:
            continue
        for sent in rev.review_sentences:
            sp.append(sent[0])
        

df = pd.DataFrame({"spoiler":sp})
df.to_csv("gr_corpus/uncleaned_sub.csv")