"""
cluster.py
"""
from collections import Counter, defaultdict, deque
import copy
import math
import matplotlib.pyplot as plt
import networkx as nx
import urllib.request
import pickle


def read_friends():
    return pickle.load(open('friends.pkl', 'rb'))


def count_friends(users):
    counts = Counter()
    for user in users:
        counts.update(user['friends'])
    return counts

def create_graph(users, friend_counts):
    graph = nx.Graph()
    parent_node='BarackObama'
    graph.add_node(parent_node)
    for user in users:
        graph.add_edge(parent_node, user["screen_name"])
    for user in users:
        graph.add_node(user["screen_name"])
        for friends in user["friends"]:
            if friend_counts[friends] > 1:
                graph.add_node(friends)
                graph.add_edge((friends), user["screen_name"])
    return graph

def draw_network(graph, users, filename):
    labels = {}
    parent_node = 'BarackObama'
    for node in graph.nodes():
        for user in users:
            if node == user["screen_name"] or node == parent_node:
                labels[node] = node

    plt.figure(figsize=(15, 15))
    nx.draw_networkx(graph, edge_color='#eeefff', labels=labels)
    plt.savefig(filename)


def girvan_newman(G, most_valuable_edge=None):
    """Finds communities in a graph using the Girvan–Newman method.

    Notes
    -----
    The Girvan–Newman algorithm detects communities by progressively
    removing edges from the original graph. The algorithm removes the
    "most valuable" edge, traditionally the edge with the highest
    betweenness centrality, at each step. As the graph breaks down into
    pieces, the tightly knit community structure is exposed and the
    result can be depicted as a dendrogram.

    """
    # If the graph is already empty, simply return its connected
    # components.
    if G.number_of_edges() == 0:
        yield tuple(nx.connected_components(G))
        return
    # If no function is provided for computing the most valuable edge,
    # use the edge betweenness centrality.
    if most_valuable_edge is None:
        def most_valuable_edge(G):
            """Returns the edge with the highest betweenness centrality
            in the graph `G`.

            """
            # We have guaranteed that the graph is non-empty, so this
            # dictionary will never be empty.
            betweenness = nx.edge_betweenness_centrality(G)
            return max(betweenness, key=betweenness.get)
    # The copy of G here must include the edge weight data.
    # Self-loops must be removed because their removal has no effect on
    # the connected components of the graph.
    G.remove_edges_from(G.selfloop_edges())
    while G.number_of_edges() > 0:
        yield _without_most_central_edges(G, most_valuable_edge)



def _without_most_central_edges(G, most_valuable_edge):
    original_num_components = nx.number_connected_components(G)
    num_new_components = original_num_components
    while num_new_components <= original_num_components:
        edge = most_valuable_edge(G)
        G.remove_edge(*edge)
        new_components = tuple(nx.connected_components(G))
        num_new_components = len(new_components)
    return new_components

def jaccard(graph, node):
    jaccard_scores = []
    neighbors = set(graph.neighbors(node))
    for n in graph.nodes():
        if node!=n and not graph.has_edge(node, n):
            neighbors2 = set(graph.neighbors(n))
            jaccard_scores.append(((node, n), len(neighbors & neighbors2) / len(neighbors | neighbors2)))
    return sorted(jaccard_scores, key=lambda x: (-x[1],x[0]))

def main():
    users = read_friends()
    friend_counts = count_friends(users)
    graph = create_graph(users, friend_counts)
    parent_node = 'BarackObama'
    draw_network(graph,users, 'network.png')
    copy_graph = graph.copy()
    jaccard_scores = jaccard(copy_graph, parent_node)
    #print(jaccard_scores)
    for (node,n), scores in jaccard_scores:
        if scores < 0.2:
            copy_graph.remove_node(n)
    draw_network(copy_graph,users, 'jaccard_Network.png')
    result = girvan_newman(copy_graph)
    communities = (tuple((c) for c in next(result)))
    f = open("cluster_output.txt", "w")
    f.write('\nNumber of communities discovered: %d' % len(communities))
    num_of_users=0
    for i in range(len(communities)):
        num_of_users+=len(communities[i])
    f.write('\nAverage number of users per community: ' + str(num_of_users/len(communities)))
    f.close()
    draw_network(copy_graph,users, 'Clustered_Network.png')
if __name__=='__main__':
    main()
