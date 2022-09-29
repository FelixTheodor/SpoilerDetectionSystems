# Spoiler Detection Systems #

This repository contains the code related to the spoiler detection systems implemented for my masters thesis. Since I cannot upload the used ebook corpus, there are some result files stored as well. These do only contain numbers and review sentences from the GoodReads dataset provided by @SpoilerNet. This README gives a quick overlook on how to run the different systems.

### Corpora
The GoodReads corpus raw files can be found in the SpoilerNet GitHub. https://github.com/MengtingWan/goodreads
Please download the full corpus and unpack it as 'gr_corpus/gr_all.json'. Some of the systems rely on this path. The sub corpus used in the thesis are stored in the gr_corpus folder.
The used ebook corpus cannot be uploaded due to copyright restrictions.
Unfortunately, many parts of the result files and remaining corpus files needed to be compressed to not exceed githubs maximum file size (100MB). You need to unpack the files in these folders before you can use the system.

### LDA10

LDA10 can be started from the main.py file. You need to set a config which is also the name under which the results are stored in the results folder. Since the raw ebook data is not available, the TopicModeller will not work (except you prepare your own corpus and store it in the book_corpus folder the way @OCTIS (https://github.com/MIND-Lab/OCTIS) needs its corpus to be stored). If you choose one of the systems that I uploaded the results to (e.g. LDA-20_10) and provide the goodreads corpus, you can use the Trainer, Validator and Presenter on the data.

### LDA1

LDA1 is not as modular under the hood. Therefore it is not possible to use the system if there is no data in the book_corpus folder. If you add book files yourself (see the helper folder for scripts to transform epubs to the OCTIS data type), you can just uncomment the LDA1 class calls in the main file and it should work. Remember to increase the number of topics though!

### SpoilerNet

The SpoilerNet implementation was done via Jupyter Notebooks and is based on torch. It is recommended to upload the SPOILERNET.ipynb file to a host like Google or Paperspace and do the work in the cloud, since some of the computations can take a while (and graphic cards speed it up quite a bit). Make sure that the needed files are uploaded as well (eg the GoodReads corpus) and stored under the right path (you can see those in the parts of code that read in the data as pd DataFrames). For preprocessing of the reviews, take a look at the _PREPROCESS.ipynb.

### Tabular Learner

This is the place were all systems are combined and evaluation of results happens. You can find the implementation of the Learner in the TABLEARNER.ipynb file. It relies on almost all the data in the data/res/ folder, so it makes sense to upload this as well to the host of your Jupyter Notebook. Here you can configure which corpus to use ('vs' == GRV, 'es' == GRA) and see how the different combinations of features perform. You can also add your own features if you created them by putting the result file in the data folder and load it in the notebook.

### Dependencies
All the code is written and run in python 3.7. There are several dependencies on third party packages. All of them are listed in the dependencies.txt. It is recommended to use a virtual environment before installing all of those. The ipynb files usually have some installation prompts included in the setup.

### Run on different systems
All the code is written on linux. If you want to make it work on a different OS, you might need to change some parts (for instance, the way the paths are written, linux uses / and windows \\).
