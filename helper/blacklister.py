# this script counts all the tokens from the preprocessed
# book corpus and returns the top 50 as a blacklist
from os import listdir

path = "book_corpus/preprocessed/"
files = listdir(path)
general_blacklist = {}

for fn in files:
    f = open(path+fn, "r")
    all_tokens = {}
    for line in f.readlines():
        tokens = line.split()
        for t in tokens:
            if t in all_tokens.keys():
                all_tokens[t] += 1
            else:
                all_tokens[t] = 1
    marklist = sorted(all_tokens.items(), key=lambda x:x[1], reverse=True)[:50]
    for el in marklist:
        if el[0] in general_blacklist.keys():
            general_blacklist[el[0]] += 1
        else:
            general_blacklist[el[0]] = 1

marklist = sorted(general_blacklist.items(), key=lambda x:x[1], reverse=True)
n_list = []
for el in marklist:
    if el[1] > 20:
        n_list.append(el[0])
print(n_list)
