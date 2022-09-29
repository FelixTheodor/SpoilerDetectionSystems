# this script takes the preprocessed ebook files and turns the content 
# into a corpus readbale by OCTIS, which means creating a vocabualry and 
# a corpus.tsv
# it also splits the original content of the book in CHUNKSIZE parts of equal length
import random
import os
import numpy as np

CHUNKSIZE = 50
blacklist = ["chapter", 'look', 'one', 'like', 'time', 'would', 'could', 'go', 'back', 'know', 'said', 'see', 'get', 'dont', 'way', 'hand', 'think', 'even', 'ask', 'thing', 'eye', 'come', 'want', 'make', 'thought', 'still', 'turn', 'head', 'im', 'didnt', 'someth', 'right', 'well', 'say', 'time', 'one', 'back', 'like', 'look', 'go', 'know', 'get', 'would', 'see', 'dont', 'could', 'said', 'way', 'want', 'think', 'even', 'hand', 'eye', 'make', 'head', 'im', 'thing', 'ask', 'come', 'still', 'didnt', 'turn', 'someth', 'tri', 'right']

def read_and_split_corpus(path, chunk_number):
    allLines = []
    with open(path, 'r') as f:
        for line in f.readlines():
            allLines.append(line)
    allLines = np.array(allLines)
    chunks = np.array_split(allLines, indices_or_sections=chunk_number)
    return chunks, allLines

def create_corpus(i, chunk, book):
    if not os.path.exists(f"book_corpus/octis/{CHUNKSIZE}/{book}/{i+1}"):
        os.makedirs(f"book_corpus/octis/{CHUNKSIZE}/{book}/{i+1}")
    corpus = open(f"book_corpus/octis/{CHUNKSIZE}/{book}/{i+1}/corpus.tsv", "w")
    vocab = open(f"book_corpus/octis/{CHUNKSIZE}/{book}/{i+1}/vocabulary.txt", "w")
    all_words = set()
    for para in chunk:
        if len([w for w in blacklist if w in para]) != 0:
            for w in blacklist:
                para = para.replace(w, "")
        if len(para.split()) == 0:
            continue
        split_n = random.randint(1,10)
        split = "train"
        if split_n == 1:
            split = "test"
        elif split_n == 2:
            split = "val"
        corpus.write(f"{para[:-2]}\t{split}\t{i+1}\n")
        for word in para.split():
            all_words.add(word)
    corpus.close()
    for w in all_words:
        vocab.write(w+"\n")
    vocab.close()

def main():
    path = "book_corpus/preprocessed/"
    dir_list = os.listdir(path)

    for book in dir_list:
        if not os.path.exists(f"book_corpus/octis/{CHUNKSIZE}/{book}"):
            os.makedirs(f"book_corpus/octis/{CHUNKSIZE}/{book}")
        chunks, all_c = read_and_split_corpus(path+book, CHUNKSIZE)
        
        create_corpus(-1, all_c, book)
        
        for i in range(0, len(chunks)):
            chunk = chunks[i]
            create_corpus(i, chunk,book)
        print(book)

main()
            
    
    

