# this script does all the preprocessing to the ebook corpus that 
# are described in detail in the thesis
# it also introduces the preprocess_word method, wich is used 
# in other places of the code, too
import nltk
from nltk.corpus import stopwords
import string
import os

def preprocess_word(word):
    word = word.lower()
    word = word.translate(str.maketrans('', '', string.punctuation))
    word = word.replace('“', "").replace("”", "").replace("’", "").replace("…", "").replace("—", "")
    if word in stopwords.words('english'):
        return ""
    return nltk.PorterStemmer().stem(word)

def preprocess_book(path, firstPerson="", anaphora=False):
    f = open("book_corpus/raw/" + path, "r")
    whole_book = ""
    all_words = []
    for line in f.readlines():
        if line.replace(" ", "") != "":
            whole_book += line + "\n"
    
    if firstPerson != "":
        whole_book = replace_char_refs(whole_book, firstPerson)
    if anaphora:
        whole_book = replace_anaphorics(whole_book)
    
    for line in whole_book.split("\n"):
        words = line.split()
        for word in words:
            word = preprocess_word(word)
            if len(word) > 0:
                all_words.append(word + " ")
        if len(words) > 1: 
            all_words.append("\n")
    f.close()
    w = open("book_corpus/preprocessed/" + path, "w")
    for word in all_words:
        w.write(word)
    w.close()

def speaking_change(word):
    signs = ['"', "'", "“", "”", "‘"]
    if len(word) == 0:
        return False
    if word[0] in signs and (len(word) == 1 or word[-1] not in signs):
        return True
    if word[-1] in signs and (len(word) == 1 or word[0] not in signs):
        return True
    return False

def replace_char_refs(book, name):
    new_book = ""
    speaking = False
    
    for line in book.split("\n"):
        words = line.split()
        #words = [word.translate(str.maketrans('', '', string.punctuation)) for word in words]
        
        for word in words:
            if speaking_change(word):
                if speaking:
                    speaking = False
                else:
                    speaking = True
            if word in ["I", "me", "mine", "my", "Me", "Mine", "My"] and not speaking:
                word = name
            new_book += word + " "
        new_book += "\n"
    return new_book

def replace_anaphorics(book):#
    pass

def main():
    all_firsts = {
        "27833670-Dark Matter (Blake Crouch).epub.txt":"Jason",
        "22557272-The Girl on the Train (Paula Hawkins).epub.txt":"Rachel",
        "18692431-Everything, Everything (Nicola Yoon).epub.txt":"Madeline",
        "18007564-The Martian (Weir, Andy).epub.txt":"Mark",
        "17182126-Steelheart-Brandon_Sanderson.epub.txt":"David",
        "15783514-The Ocean at the End of the Lane (Gaiman, Neil).epub.txt":"Narrator Protagonist",
        "13596166-Joyland (Stephen King).epub.txt":"Devin",
        "11870085-The Fault in Our Stars (John Green).epub.txt":"Hazel",
        "9969571-Ready Player One (Ernest Cline).epub.txt":"Wade",
        "2767052-The Hunger Games 1 - The Hunger Games (Suzanne Collins).epub.txt":"Katniss",
        "1215032-The Wise Mans Fear (Patrick Rothfuss).epub.txt":"Kvothe",
        "186074-The Name of the Wind (Patrick Rothfuss).epub.txt":"Kvothe",
        "157993-The Little Prince (Antoine de Saint-Exupéry).epub.txt":"Narrator Pilot Protagonist",
        "91477-Dresden Files 02 - Fool Moon (Butcher, Jim).epub.txt":"Harry Dresden",
        "77197-Assassin's Apprentice - Robin Hobb.epub.txt":"Fitz",
        "47212-Storm_Front.epub.txt":"Harry Dresden",
        "29044-Donna Tartt - The Secret History.txt":"Richard",
        "16143347-We Were Liars (Emily Lockhart)).epub.txt":"Cadence",
        "20698530-P.S. I Still Love You (Jenny Han [Han, Jenny]).epub.txt":"Lara",
        "22328546-Red Queen (Red Queen 1) (Victoria Aveyard).epub.txt":"Mare",
        "22544764-Uprooted (Naomi Novik).epub.txt":"Agnieszka",
        "27362503-It Ends with Us (Colleen Hoover).epub.txt":"Lily",
        "16096824-A Court of Thorns and Roses (A Court of Thorns and Roses 1) (Sarah J. Maas [Maas, Sarah J.]).epub.txt":"Feyre"
        }
    path = "book_corpus/raw/"
    all_books = os.listdir(path)
    
    for book in all_books:
        print(book)
        name = "" if book not in all_firsts.keys() else all_firsts[book]
        preprocess_book(book, firstPerson=name)
    print("Finished")

if __name__ == "__main__":
    main()