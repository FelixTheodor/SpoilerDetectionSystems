# this script adds paragraphs to the epub files that miss them

paths = [
    "13596166-Joyland (Stephen King).epub.txt",
    "186074-The Name of the Wind (Patrick Rothfuss).epub.txt",
    "16793-Stardust (Neil Gaiman).epub.txt",
    "2767793-The Hero of Ages (Brandon Sanderson).epub.txt",
    "18775247-Mr. Mercedes (Stephen King).epub.txt",
    "68429-The Well of Ascension (Brandon Sanderson).epub.txt"
]

for path in paths:

    w = open(path, "w")

    f = open("book_corpus/raw/"+path, "r")

    for line in f.readlines():
        line = line.split(".")
        para = []
        for sent in line:
            if len(para) == 3:
                for s in para:
                    w.write(s+".")
                w.write("\n")
                para = [sent[1:]]
            else:
                para.append(sent)
        for s in para:
            w.write(s+".")
    w.close()
    f.close() 