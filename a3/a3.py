# coding: utf-8

# # Assignment 3:  Recommendation systems
#
# Here we'll implement a content-based recommendation algorithm.
# It will use the list of genres for a movie as the content.
# The data come from the MovieLens project: http://grouplens.org/datasets/movielens/

# Please only use these imports.
from collections import Counter, defaultdict
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
import urllib.request
import zipfile

def download_data():
    """ DONE. Download and unzip data.
    """
    url = 'https://www.dropbox.com/s/h9ubx22ftdkyvd5/ml-latest-small.zip?dl=1'
    urllib.request.urlretrieve(url, 'ml-latest-small.zip')
    zfile = zipfile.ZipFile('ml-latest-small.zip')
    zfile.extractall()
    zfile.close()


def tokenize_string(my_string):
    """ DONE. You should use this in your tokenize function.
    """
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(movies):
    """
    Append a new column to the movies DataFrame with header 'tokens'.
    This will contain a list of strings, one per token, extracted
    from the 'genre' field of each movie. Use the tokenize_string method above.

    Note: you may modify the movies parameter directly; no need to make
    a new copy.
    Params:
      movies...The movies DataFrame
    Returns:
      The movies DataFrame, augmented to include a new column called 'tokens'.

    >>> movies = pd.DataFrame([[123, 'Horror|Romance'], [456, 'Sci-Fi']], columns=['movieId', 'genres'])
    >>> movies = tokenize(movies)
    >>> movies['tokens'].tolist()
    [['horror', 'romance'], ['sci-fi']]
    """
    new_list = []
    for i in movies['genres']:
        new_list.append(tokenize_string(i))
    movies['tokens'] = new_list
    return movies


def featurize(movies):
    """
    Append a new column to the movies DataFrame with header 'features'.
    Each row will contain a csr_matrix of shape (1, num_features). Each
    entry in this matrix will contain the tf-idf value of the term, as
    defined in class:
    tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    where:
    i is a term
    d is a document (movie)
    tf(i, d) is the frequency of term i in document d
    max_k tf(k, d) is the maximum frequency of any term in document d
    N is the number of documents (movies)
    df(i) is the number of unique documents containing term i

    Params:
      movies...The movies DataFrame
    Returns:
      A tuple containing:
      - The movies DataFrame, which has been modified to include a column named 'features'.
      - The vocab, a dict from term to int. Make sure the vocab is sorted alphabetically as in a2 (e.g., {'aardvark': 0, 'boy': 1, ...})
    """

    list_for_vocab = []
    new_list = []
    vocab = defaultdict(lambda: 0)
    for i in range(len(movies)):
        list_for_vocab.append(movies['tokens'][i])
    list_for_vocab = [vocab for sublist in list_for_vocab for vocab in sublist]
    c = 0
    for k in sorted(set(list_for_vocab)):
        vocab[k] = c
        c += 1

    new_count = Counter()
    for i in list(movies['tokens']):
        new_count.update(set(i))

    for j in range(len(movies)):
        count = Counter()
        count.update(movies['tokens'][j])
        new_sorted = sorted(movies['tokens'][j])
        partA = defaultdict(lambda: 0)
        row = []
        col = []
        data = []
        temp_storage = []
        for i in range(len(new_sorted)):
            if new_sorted[i] not in temp_storage:
                temp_storage.append(new_sorted[i])
                partA[new_sorted[i]] = (count[new_sorted[i]] / max(count.values())) * math.log10(
                    len(movies) / new_count[new_sorted[i]])
                col.append(vocab[new_sorted[i]])
                row.append(0)
                data.append(partA[new_sorted[i]])
        new_list.append(csr_matrix((data, (row, col)), shape=(1, len(vocab))))
    movies['features'] = pd.Series(new_list, index=movies.index)
    return tuple((movies, vocab))

def train_test_split(ratings):
    """DONE.
    Returns a random split of the ratings matrix into a training and testing set.
    """
    test = set(range(len(ratings))[::1000])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]


def cosine_sim(a, b):
    """
    Compute the cosine similarity between two 1-d csr_matrices.
    Each matrix represents the tf-idf feature vector of a movie.
    Params:
      a...A csr_matrix with shape (1, number_features)
      b...A csr_matrix with shape (1, number_features)
    Returns:
      The cosine similarity, defined as: dot(a, b) / ||a|| * ||b||
      where ||a|| indicates the Euclidean norm (aka L2 norm) of vector a.
    """
    return (a.toarray()).dot(((b.toarray())).transpose()) / (np.sqrt(a.multiply(a).sum(1))).dot(
        (np.sqrt(b.multiply(b).sum(1))).transpose())

def make_predictions(movies, ratings_train, ratings_test):
    """
    Using the ratings in ratings_train, predict the ratings for each
    row in ratings_test.

    To predict the rating of user u for movie i: Compute the weighted average
    rating for every other movie that u has rated.  Restrict this weighted
    average to movies that have a positive cosine similarity with movie
    i. The weight for movie m corresponds to the cosine similarity between m
    and i.

    If there are no other movies with positive cosine similarity to use in the
    prediction, use the mean rating of the target user in ratings_train as the
    prediction.

    Params:
      movies..........The movies DataFrame.
      ratings_train...The subset of ratings used for making predictions. These are the "historical" data.
      ratings_test....The subset of ratings that need to predicted. These are the "future" data.
    Returns:
      A numpy array containing one predicted rating for each element of ratings_test.
    """
    list_of_pred=[]
    for user, rating in zip(ratings_test['userId'], ratings_test['movieId']):
        avg_sum = []
        cosine_sum = []
        ratings_for_zero_val=[]
        for index, row in ratings_train[ratings_train.userId==user].iterrows():
            ratings_for_zero_val.append(row.rating)
            cosinesim = cosine_sim(movies['features'][movies[movies.movieId==row.movieId].index[0]],
                                   movies['features'][movies[movies.movieId==rating].index[0]])
            if cosinesim > 0:
                avg_sum.append(row.rating * cosinesim)
                cosine_sum.append(cosinesim)
        if(len(avg_sum)):
            list_of_pred.append(np.sum(avg_sum)/np.sum(cosine_sum))
        else:
            list_of_pred.append(np.mean(ratings_for_zero_val))
    return np.array(list_of_pred)


def mean_absolute_error(predictions, ratings_test):
    """DONE.
    Return the mean absolute error of the predictions.
    """
    return np.abs(predictions - np.array(ratings_test.rating)).mean()


def main():
    download_data()
    path = 'ml-latest-small'
    ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
    movies = pd.read_csv(path + os.path.sep + 'movies.csv')
    movies = tokenize(movies)
    movies, vocab = featurize(movies)
    print('vocab:')
    print(sorted(vocab.items())[:10])
    ratings_train, ratings_test = train_test_split(ratings)
    print('%d training ratings; %d testing ratings' % (len(ratings_train), len(ratings_test)))
    predictions = make_predictions(movies, ratings_train, ratings_test)
    print('error=%f' % mean_absolute_error(predictions, ratings_test))
    print(predictions[:10])


if __name__ == '__main__':
    main()
