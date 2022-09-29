# this script turns epub files to txt files
from epub2txt import epub2txt
import os
 
# Get the list of all files and directories
checkpath = "book_corpus/raw/"
path = "new_epubs/"
dir_list = os.listdir(path)
check_list = os.listdir(checkpath)

print(f"found {len(dir_list)} epubs")

for p in check_list:
    p = p[:-4]
    if p in dir_list:
        dir_list.remove(p)

print(f"work with {len(dir_list)} epubs")
 
for p in dir_list:
    print(p)
    res = epub2txt(path+p)
    w = open(f"book_corpus/raw/{p}.txt", 'w')
    w.write(res)
    w.close()