# this script calclulates some basics stats about the used book_corpus
import os

path = "book_corpus/preprocessed/"
dir_list = os.listdir(path)

all_docs = 0
all_len = 0
all_book = len(dir_list)

for book in dir_list:
    f = open(path + book, "r")
    b_docs = 0
    b_len = 0
    for line in f.readlines():
        b_len += 1
        b_docs += len(line.split())
    all_docs += b_docs
    all_len += b_len
    b_avg = b_docs / b_len
    if b_avg > 200 or b_avg < 10:
        print(book)
        print(f"{b_avg} tokens in {b_len} docs.\n")

all_avg = all_docs / all_len
print("###")
print(f"{all_avg} tokens in {all_docs} docs.")
    