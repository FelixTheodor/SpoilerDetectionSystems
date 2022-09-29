# this book takes a list of all the used book ids as well 
# as the original goodreads corpus and prunes the corpus 
# so that only reviews related to the bookIDs remain
from msgspec.json import decode, encode
from review_struct import Review
import random
from preprocess import preprocess_word


def copy(rev, part, ps):
    return Review(book_id=rev.book_id, has_spoiler=rev.has_spoiler, rating=rev.rating,
                  review_sentences=rev.review_sentences, user_id = rev.user_id, 
                  partition=part, preprocessed_sentences=ps)

def preprocess_review(rev):
    new_sents = []
    for sent in rev.review_sentences:
        new_sent = ""
        for w in sent[1].split():
            w = preprocess_word(w)
            if len(w) > 0:
                new_sent += w + " "
        new_sents.append([sent[0],new_sent[:-1]])
    return new_sents

all_relevant_ids = []
with open("book_corpus/meta/final_book_ids1.txt", "r") as f:
    for line in f.readlines():
        if "-" in line:
            all_relevant_ids.append(line.split("-")[0])
        if "." in line:
            all_relevant_ids.append(line.split(".")[0])

print(len(all_relevant_ids))

folder = "gr_corpus/"
with open(folder+"uncleaned_sub.json", "rb") as f:
    w_all = open(folder+"un_sub_corpus.json", "wb")
    count = 0
    scount = 0
    for line in f.readlines():
        review = decode(line, type=Review)
        bid = review.book_id
        sp = review.has_spoiler
        part = "NONE"
        if bid in all_relevant_ids:
            pre = preprocess_review(review)
            split_n = random.randint(1,10)
            if split_n == 1 or split_n == 2:
                part = "VAL"
            elif split_n == 3:
                part = "TST"
            else:
                part = "TRN"
            rev = copy(review, part, pre)
            w_all.write(encode(rev) + bytes("\n", "utf-8"))

    w_all.close()


    