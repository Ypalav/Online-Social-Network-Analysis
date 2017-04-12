"""
collect.py
"""
from collections import Counter
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
import re, os
from TwitterAPI import TwitterAPI
import pickle

consumer_key = 'qlYfxqC7I4qPuWvvJ3nfv6WeA'
consumer_secret = 'Yn5AdOwi9pBdIfVDpXE1Rsmdk4ftbqxzCIMhIQm8WcVGqlV1HA'
access_token = '102416816-4zdjoCHfvLrEP5EybPiInaIUzNnMqaGd2GlXqBqM'
access_token_secret = 'nItvwfutUkDWagkSpNchoQ6dPZsTLOKKGNIkJ0RalkqgF'


def get_twitter():
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def robust_request(twitter, resource, params, max_tries=5):
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)

def get_mentions(twitter):
    mentions = []
    while True:
        request = robust_request(twitter, "search/tweets", {"q":'@BarackObama', "count": 100, "lang":'en'})
        for item in request.get_iterator():
            mentions.append(item)
        if len(mentions) > 100:
            break
    #print(len(mentions))
    return mentions

def get_tweets(twitter, users):
    tweets=[]
    loop_range = 5
    for user in range(len(users)):
        for i in range(1, loop_range):
            request = twitter.request('statuses/user_timeline',
                                      {'screen_name': users[user]['screen_name'], 'count': 200, 'include_rts': 'false', 'page':i})
            tweets.append(request)
    pickle.dump(tweets, open('tweets_data.pkl', 'wb'))

def get_friends(twitter, user):
    request = robust_request(twitter, "friends/ids", {"screen_name": user, "count": 5000})
    friends = [friend for friend in request]
    return (sorted(friends))

def add_all_friends(twitter, users, num):
    for user in range(len(users)):
        users[user]['friends'] = get_friends(twitter, users[user]['screen_name'])
        num += len(users[user]['friends'])
        pickle.dump(users, open('friends.pkl', 'wb'))
    return num

def get_users(users_object):
    users = []
    temp_users=[]
    for tweet in range(len(users_object)):
        new_user = users_object[tweet]['user']['screen_name']
        if new_user not in temp_users and len(temp_users)<=10:
            temp_users.append(new_user)
            user_list = {}
            user_list['screen_name'] = new_user
            users.append(user_list)

    #print('Total friends', len(users))
    return users


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
    return val

def main():
    twitter = get_twitter()
    users_object = get_mentions(twitter)
    users = get_users(users_object)
    num=0
    num_of_friends=len(users)
    num_of_friends += add_all_friends(twitter, users, num)
    get_tweets(twitter, users)
    tweets = read_file()
    num_of_tweets = create_files(tweets)
    f = open("collect_output.txt", "w")
    f.write("Number of users collected: " + str(num_of_friends))
    f.write("\nNumber of messages collected: " + str(num_of_tweets))
    f.close()

if __name__=='__main__':
    main()