"""
classify.py
"""
import re
import numpy as np
import pickle
import os

def read_file():
    return pickle.load(open('tweets_data.pkl', 'rb'))

def create_files(tweets):
    directory='tweets_data_new'
    if not os.path.exists(directory):
        os.makedirs(directory)
    val=0
    for i in tweets:
        for tweet in i:
            f = open(("tweets_data_new/20359372" + "OSNA" + str(val) + ".txt"), "w", encoding='utf8')
            f.write(tweet['text'])
            f.close
            val+=1

def tokenize(t):
    text = t.lower()
    text = re.sub('@\S+', ' ', text)  # Remove mentions.
    text = re.sub('http\S+', ' ', text)  # Remove urls.
    return re.findall('[A-Za-z]+', text) # Retain words.

def download_afinn():
    from collections import defaultdict
    from io import BytesIO
    from zipfile import ZipFile
    from urllib.request import urlopen

    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    afinn_file = zipfile.open('AFINN/AFINN-111.txt')

    afinn = dict()

    for line in afinn_file:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])

    return afinn

def afinn_sentiment2(terms, afinn, verbose=False):
    pos = 0
    neg = 0
    for t in terms:
        if t in afinn:
            if afinn[t] > 0:
                pos += afinn[t]
            else:
                neg += -1 * afinn[t]
    return pos, neg

def get_files(path):
    text_files = [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.txt')]
    return sorted(text_files)

def read_tokenize(all_train_files):
    if (isinstance(all_train_files, list) == False):
        all_train_files = all_train_files.tolist()

    new_list = []
    tweets = []
    for f in all_train_files:
        file = open(f, 'r', encoding='utf8')
        new_tweet = str(file.read())
        tweets.append(new_tweet)
        new_list.append(tokenize(new_tweet))

    return new_list, tweets

def classify(new_list, tweets):
    positives = []
    negatives = []
    new_path = 'Classified'
    afinn=download_afinn()
    val = 0
    for token_list, tweet in zip(new_list, tweets):
        pos, neg = afinn_sentiment2(token_list, afinn)
        if pos > neg:
            positives.append((tweet, pos, neg))
        elif neg > pos:
            negatives.append((tweet, pos, neg))
    f = open("classify_output.txt", "w")
    f.write("\nNumber of instances(tweets) per class found:-")
    f.write("\nPositive Class: "+ str(len(positives)))
    f.write("\nNegative Class: "+ str(len(negatives)))
    f.write("\nOne example from each class:-")
    f.write("\nPositive Class: "+ str(sorted(positives, key=lambda x: x[1], reverse=True)[:1]))
    f.write("\nNegative Class: "+ str(sorted(negatives, key=lambda x: x[2], reverse=True)[:1]))
    f.close

def main():
    path = 'tweets_data_new/'
    all_train_files = get_files(path)
    new_list, tweets = read_tokenize(all_train_files)
    classify(new_list, tweets)

if __name__=='__main__':
    main()