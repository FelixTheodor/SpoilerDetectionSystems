# this script calculates some basic stats about the ebook and goodreads corpus

from os import listdir
import pandas as pd

word_count = 0
para_count = 0

p= "book_corpus/octis/10/"
for folder in listdir(p):
    path = f"{p}{folder}/0/corpus.tsv"
    with open(path) as f:
        for line in f.readlines():
            para_count += 1
            for word in line.split():
                word_count += 1
#print(para_count)
#print(word_count)

df = pd.read_json("gr_corpus/cp_sub_corpus.json", lines=True)

revs = len(df)
sents = 0
spoiler = 0
all_pos = 0
chunk_num = 0
chunk_size = 0

for _,row in df.iterrows():
    i = 0
    found = False
    chunk = 0
    for sent in row.review_sentences:
        i += 1
        sents += 1
        if sent[0] == 1:
            if found:
                chunk += 1
            else:
                found = True
                chunk = 1
                chunk_num +=1
            spoiler += 1
            all_pos += i / len(row.review_sentences)
        else:
            if found:
                found = False
                chunk_size += chunk
print(revs)
print(sents)
print(spoiler)
print(all_pos / spoiler)
print(chunk_size/chunk_num)