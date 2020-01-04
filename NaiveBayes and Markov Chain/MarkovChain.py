#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 16:48:43 2019

@author: shaivalshah
"""

import glob
import re
import sys
from numpy.random import choice

class MarkovChain:
    def __init__(self, aut_dir, stem_word_file, prob_file):
        self.aut_dir = aut_dir
        self.stem_word_file = stem_word_file
        self.prob_file = prob_file
        self.stop_words = set()
        self.unigram = dict()
        self.bigram = dict()
        self.trigram = dict()
    
    #generate the list of stop words
    def getStopWords(self):
        with open(self.stem_word_file, 'r') as f:
            for word in f.readlines():
                self.stop_words.add(word.replace('\n', ''))
            f.close()
            
    #Function to remove stop words
    def removeStopWords(self, corpus):
        self.getStopWords()
        corpus = [
                word.strip() for word in corpus
                if word not in self.stop_words and len(word) != 0
            ]
        return corpus
    
    #This function updates the unigram dictionary using the corpus passed as an argument
    def updateUnigram(self, corpus):
        for word in corpus:
            self.unigram[word] = self.unigram[word] + 1 if word in self.unigram else 1
    
    #This function updates the bigram dictionary using the corpus passed as an argument
    def updateBigram(self, corpus):
        for i in range(len(corpus) - 1):
            if corpus[i] in self.bigram:
                if corpus[i + 1] in self.bigram[corpus[i]]:
                    self.bigram[corpus[i]][corpus[i + 1]] += 1
                else:
                    self.bigram[corpus[i]][corpus[i + 1]] = 1
            else:
                self.bigram[corpus[i]] = dict()
                self.bigram[corpus[i]][corpus[i + 1]] = 1
    
    #This function updates the trigram dictionary using the corpus passed as an argument
    def updateTrigram(self, corpus):
        for i in range(len(corpus) - 2):
            if corpus[i] in self.trigram:
                if corpus[i + 1] in self.trigram[corpus[i]]:
                    if corpus[i + 2] in self.trigram[corpus[i]][corpus[i + 1]]:
                        self.trigram[corpus[i]][corpus[i + 1]][corpus[i + 2]] += 1
                    else:
                        self.trigram[corpus[i]][corpus[i + 1]][corpus[i + 2]] = 1
                else:
                    self.trigram[corpus[i]][corpus[i + 1]] = dict()
                    self.trigram[corpus[i]][corpus[i + 1]][corpus[i + 2]] = 1
            else:
                self.trigram[corpus[i]] = dict()
                self.trigram[corpus[i]][corpus[i + 1]] = dict()
                self.trigram[corpus[i]][corpus[i + 1]][corpus[i + 2]] = 1
    
    #This function preprocess text data, remove stop words and punctuations and updates unigram, bigram and trigram
    def preprocessData(self):
        self.getStopWords()
        for file in glob.glob(self.aut_dir + '/*.txt'):
            with open(file, 'r') as f:
                lines = f.readlines()
                corpus = ' '.join(lines)
                corpus = re.sub(r"[\:\-\(\)\[\]\{\}\’\'\"\“\”\n\t\/\\]", " ", corpus).lower()
                corpus = re.sub('[\;|\.|\?|\!\,]', '', corpus).lower()
                corpus = corpus.split()
                corpus = self.removeStopWords(corpus)
                self.updateUnigram(corpus)
                self.updateBigram(corpus)
                self.updateTrigram(corpus)
    
    #After all the files are processed this function is called to change the frequency in unigram,
    #bigram and trigram into probability
    def calcProb(self):
        for word, next_first_word_dict in self.trigram.items():
            for next_first_word, next_second_word_dict in next_first_word_dict.items():
                total = self.bigram[word][next_first_word]
                for next_second_word, freq in next_second_word_dict.items():
                    self.trigram[word][next_first_word][
                        next_second_word] = freq / total
        for word, next_word_dict in self.bigram.items():
            total = self.unigram[word]
            for next_word, freq in next_word_dict.items():
                self.bigram[word][next_word] = freq / total
        total = sum(self.unigram.values())
        for word, freq in self.unigram.items():
            self.unigram[word] = freq / total

    #This function writes the probabilities of all unigram, bigram and trigram in the prob_file
    #passed in the argument
    def outputProbFile(self):
        with open(self.prob_file, 'w') as f:
            f.write("-" * 30 + "Unigram Probabilities" + "-" * 30 + "\n")
            for word, prob in self.unigram.items():
                f.write("P({}) = {}\n".format(word, prob))
            f.write("\n" + "-" * 30 + "Bigram Probabilities" + "-" * 30 + "\n")
            for word, next_word_dict in self.bigram.items():
                for next_word, prob in next_word_dict.items():
                    f.write("P({} | {}) = {}\n".format(next_word, word, prob))
            f.write("\n" + "-" * 30 + "Trigram Probabilities" + "-" * 30 + "\n")
            for word, next_first_word_dict in self.trigram.items():
                for next_first_word, next_second_word_dict in next_first_word_dict.items():
                    for next_second_word, prob in next_second_word_dict.items():
                        f.write("P({} | {} {}) = {}\n".format(
                            next_second_word, word, next_first_word, prob))
    
    #This functions calls the above functions in correct order to get all probabilities in model
    def train(self):
        self.preprocessData()
        self.calcProb()
        self.outputProbFile()


# Function to generate sentences from the model using unigram, bigram and trigram and write in the file
def generateSentence(result_file, model1, model2=None):
    with open(result_file, 'w') as f:
        if model2 is None:
            for _ in range(10):
                first_word = choice(list(model1.unigram.keys()), p = list(model1.unigram.values()))
                while first_word not in model1.bigram or first_word not in model1.trigram:
                    first_word = choice(list(model1.unigram.keys()), p = list(model1.unigram.values()))
                second_word = choice(list(model1.bigram[first_word].keys()), p = list(model1.bigram[first_word].values()))
                sentence = first_word + " " + second_word
                prob = model1.unigram[first_word] * model1.bigram[first_word][
                    second_word]
                word1 = first_word
                word2 = second_word
                for _ in range(18):
                    next_word = choice(list(model1.trigram[word1][word2].keys()), p = list(model1.trigram[word1][word2].values()))
                    # if word not present in the trigram then break the sentence
                    if word2 not in model1.trigram or next_word not in model1.trigram[word2]:
                        break
                    sentence = sentence + " " + next_word
                    prob = prob * model1.trigram[word1][word2][next_word]
                    word1 = word2
                    word2 = next_word
                f.write("Sentence: {}\n".format(sentence))
                f.write("Probability: {}\n\n".format(prob))
        else:
            f.write("Sentences from author directory 1\n\n")
            for _ in range(10):
                first_word = choice(list(model1.unigram.keys()), p = list(model1.unigram.values()))
                while first_word not in model1.bigram or first_word not in model1.trigram:
                    first_word = choice(list(model1.unigram.keys()), p = list(model1.unigram.values()))
                second_word = choice(list(model1.bigram[first_word].keys()), p = list(model1.bigram[first_word].values()))
                sentence = first_word + " " + second_word
                prob1 = model1.unigram[first_word] * model1.bigram[first_word][second_word]
                if first_word in model2.unigram:
                    if second_word in model2.bigram[first_word]:
                        prob2 = model2.unigram[first_word] * model2.bigram[first_word][second_word]
                    else:
                        prob2 = model2.unigram[first_word] * 0.001
                else: 
                    prob2 = 0.001 * 0.001
                word1 = first_word
                word2 = second_word
                for _ in range(18):
                    next_word = choice(list(model1.trigram[word1][word2].keys()), p = list(model1.trigram[word1][word2].values()))
                    # if word not present in the trigram then break the sentence
                    if word2 not in model1.trigram or next_word not in model1.trigram[word2]:
                        break
                    sentence = sentence + " " + next_word
                    prob1 = prob1 * model1.trigram[word1][word2][next_word]
                    prob2 = prob2 * model2.trigram[word1][word2][
                            next_word] if word1 in model2.trigram and word2 in model2.trigram[word1] and next_word in model2.trigram[word1][word2] else prob2*0.001
                    word1 = word2
                    word2 = next_word
                f.write("Sentence: {}\n".format(sentence))
                f.write("Probability of aut_dir1: {}\n".format(prob1))
                f.write("Probability of aut_dir2: {}\n\n".format(prob2))
            f.write("\nSentences from author directory 2\n\n")
            for _ in range(10):
                first_word = choice(list(model2.unigram.keys()), p = list(model2.unigram.values()))
                while first_word not in model2.bigram or first_word not in model2.trigram:
                    first_word = choice(list(model2.unigram.keys()), p = list(model2.unigram.values()))
                second_word = choice(list(model2.bigram[first_word].keys()), p = list(model2.bigram[first_word].values()))
                sentence = first_word + " " + second_word
                prob2 = model2.unigram[first_word] * model2.bigram[first_word][second_word]
                if first_word in model1.unigram:
                    if second_word in model1.bigram[first_word]:
                        prob1 = model1.unigram[first_word] * model1.bigram[first_word][second_word]
                    else:
                        prob1 = model1.unigram[first_word] * 0.001
                else: 
                    prob1 = 0.001 * 0.001
                word1 = first_word
                word2 = second_word
                for _ in range(18):
                    next_word = choice(list(model2.trigram[word1][word2].keys()), p = list(model2.trigram[word1][word2].values()))
                    # if word not present in the trigram then break the sentence
                    if word2 not in model2.trigram or next_word not in model2.trigram[word2]:
                        break
                    sentence = sentence + " " + next_word
                    prob2 = prob2 * model2.trigram[word1][word2][next_word]
                    prob1 = prob1 * model1.trigram[word1][word2][
                            next_word] if word1 in model1.trigram and word2 in model1.trigram[word1] and next_word in model1.trigram[word1][word2] else prob1*0.001
                    word1 = word2
                    word2 = next_word
                f.write("Sentence: {}\n".format(sentence))
                f.write("Probability of aut_dir2: {}\n".format(prob2))
                f.write("Probability of aut_dir1: {}\n\n".format(prob1))


if __name__ == "__main__":
    stop_word_file = 'EnglishStopwords.txt'
    if len(sys.argv) == 4:
        aut_dir = sys.argv[1]
        prob_file = sys.argv[2]
        result_file = sys.argv[3]
        model = MarkovChain(aut_dir, stop_word_file, prob_file)
        model.train()
        generateSentence(result_file, model)
    elif len(sys.argv) == 6:
        aut_dir1 = sys.argv[1]  
        aut_dir2 = sys.argv[2]
        prob_file1 = sys.argv[3]
        prob_file2 = sys.argv[4]
        result_file = sys.argv[5]
        model1 = MarkovChain(aut_dir1, stop_word_file, prob_file1)
        model1.train()
        model2 = MarkovChain(aut_dir2, stop_word_file, prob_file2)
        model2.train()
        generateSentence(result_file, model1, model2)
    else:
        print("Arguments not given properly\n")
        print("USAGE:\n")
        print("python MarkovChain.py aut_dir prob_file.txt result_file.txt\n")
        print("OR\n")
        print(
            "python MarkovChain.py aut_dir aut_dir2 prob1.txt prob2.txt rfile.txt"
        )
