# this script creates an input file for gensims word2vec 
# from the preprocessed book corpus
import os

w = open("word2vec_input.txt", "a")
scount = 0
tcount = 0

path = "book_corpus/preprocessed/"
all_books = os.listdir(path)

for book in all_books:
    print(book)
    with open(path+book, "r") as f:
        for line in f.readlines():
            scount += 1
            tcount += len(line.split())-1
            w.write(line)
w.close()

print(f"Sents: {scount}\nWords: {tcount}")