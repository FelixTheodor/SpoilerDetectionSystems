# this script reads a file with all the used book ids,
# a file with sentences that are marked as spoilers but are actually none 
# as well as a file with sentences that are not marked as spoilers but should be
# and cleans the sub corpus by correcting the sentences
from msgspec.json import decode, encode
from review_struct import Review
import string
from tqdm import tqdm

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

def get_number_of_sp(corpus, ids):
    num = 0
    a_num = 0
    all_books = {k:v for (k,v) in zip(ids, [[0,0] for i in range(len(ids))])}
    for rev in corpus:
        for sent in rev.review_sentences:
            if sent[0] == 1:
                num += 1
                all_books[rev.book_id][1] += 1
            all_books[rev.book_id][0] += 1
            a_num +=1
    marklist = sorted(all_books.items(), key=lambda x:x[1], reverse=True)
    return num, a_num

def fix_sent(sent, w2):
    i = input(sent[1]+ "\n--- n,b")
    fn = False
    if "n" in i:
        sent[0] = 0
        w2.write(sent[1] + "\n")
    if "b" in i:
        fn = True
    return sent, fn

def process(line):
    line = line.translate(str.maketrans('', '', string.punctuation))
    return line.lower()

ids = get_ids()
corpus = load_corpus("gr_corpus/gr_all.json", ids)

non_spoiler_sents = []
for line in open("gr_corpus/non_spoiler_sents.txt", "r").readlines():
    non_spoiler_sents.append(process(line).replace("\n",""))
#non_spoiler_sents = []
actually_spoiler_sents = []
for line in open("gr_corpus/actually_spoiler_sents.txt", "r").readlines():
    actually_spoiler_sents.append(process(line).replace("\n",""))
#actually_spoiler_sents = []

w = open("gr_corpus/uncleaned_sub.json", "wb")
c1 = 0
c2 = 0

for rev in tqdm(corpus):
    if rev.book_id not in ids:
        continue
    all_sents = []
    for sent in rev.review_sentences:
        if sent[0] == 1 and process(sent[1]) in non_spoiler_sents:
            sent[0] = 0
            c1 += 1
        if sent[0] == 0 and process(sent[1]) in actually_spoiler_sents:
            sent[0] = 1
            #actually_spoiler_sents.remove(sent[1])
            c2 += 1
        all_sents.append(sent)
    rev.review_sentences = all_sents
    w.write(encode(rev) + bytes("\n", "utf-8"))

print(c1)
print(c2)
