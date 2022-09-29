# this script calculates some general stats about the goodreads corpus
from msgspec.json import decode, encode
from review_struct import Review

all_relevant_ids = []
with open("book_corpus/meta/final_book_ids1.txt", "r") as f:
    for line in f.readlines():
        if "-" in line:
            all_relevant_ids.append(line.split("-")[0])
        if "." in line:
            all_relevant_ids.append(line.split(".")[0])
all_changed_sents = []
with open("gr_corpus/changed_sents.txt", "r") as f:
    for line in f.readlines():
        all_changed_sents.append(line.split("\n")[0])

class Counter():
    def __init__(self, name):
        self.name = name
        self.all_revs = 0
        self.all_sp_revs = 0
        self.all_sents = 0
        self.all_sp_sents = 0
        self.uids = set()
    
    def to_tsv(self):
        padder = (8 - len(self.name)) * " "
        return f"{self.name}{padder}\t\t{self.all_revs}\t{self.all_sp_revs}\t{self.all_sents}\t{self.all_sp_sents}"

all_cs = {}
for n in all_relevant_ids:
    all_cs[n] = Counter(n)
gc = Counter("general")

all_spoiler_spans = 0
all_position_of_spoilers = 0
ch_sent_count = 0

folder = "gr_corpus/"
with open(folder+"gr_all.json", "rb") as f:
    for line in f.readlines():
        #print(line)
        review = decode(line, type=Review)
        bid = review.book_id
        if bid not in all_relevant_ids:
            continue
        sp = review.has_spoiler
        uid = review.user_id
        all_cs[bid].all_revs += 1
        gc.all_revs += 1
        all_cs[bid].uids.add(uid)
        gc.uids.add(uid)
        if sp:
            all_cs[bid].all_sp_revs += 1
            gc.all_sp_revs += 1
        last_spoiler = False
        sent_count = 0
        for sent in review.review_sentences:
            if sent[0] == 1 and sent[1] in all_changed_sents:
                ch_sent_count += 1
            sent_count += 1
            all_cs[bid].all_sents += 1
            gc.all_sents += 1
            if sent[0] == 1 and sent[1] not in all_changed_sents:
                if not last_spoiler:
                    all_spoiler_spans +=1
                all_cs[bid].all_sp_sents += 1
                gc.all_sp_sents += 1
                all_position_of_spoilers += sent_count / len(review.review_sentences)
                last_spoiler = True
            else:
                last_spoiler = False

w = open("book_corpus/meta/counts.tsv", "w")
for k in all_cs.keys():
    w.write(all_cs[k].to_tsv() + "\n")
w.write(gc.to_tsv())
w.close()

print(f"avg len of spoiler spans: {gc.all_sp_sents/all_spoiler_spans}")
print(f"avg pos of spoiler sents: {all_position_of_spoilers/gc.all_sp_sents}")
print(ch_sent_count)
print(len(all_changed_sents))