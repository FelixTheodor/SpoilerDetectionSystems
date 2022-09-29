# this is an example script on how to train word vectors in gensim
import gensim

print("lets go")

input_path = "word2vec_input.txt"

docs = []
with open(input_path, "r") as f:
    for line in f.readlines():
        docs.append(line.split())

with open("word2vec_input2.txt", "r") as f:
    for line in f.readlines():
        docs.append(line.split())

#docs = list(docs)
print(f"read docs to RAM: {len(docs)}")

model = gensim.models.Word2Vec(
        docs,
        vector_size=200,
        window=10,
        min_count=1,
        workers=10)
print("created model")

word_vectors = model.wv

word_vectors.save_word2vec_format("word2vec.gz", binary=True)
print("saved model")