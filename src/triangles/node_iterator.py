from sys import argv, path
path.append('..')
from parsers import CSVParser
import utils
import numpy as np
import pickle
from time import time
import matplotlib.pyplot as plt


class NodeIterator():

  # naive attempt to get the pickled file..
  # input_path = len(argv) > 1 and argv[1] or '../tmp/frequent_itemsets.out'

  @classmethod
  def __add_to_graph(self, pair, G):
    """
    Add a sorted tuple (a, b_i) to a graph (adjacency list)
    with key:a, and values: [b1,b2,...,bn]
    """
    if G.has_key(pair[0]):
      G[pair[0]].append(pair[1])
    else:
      G[pair[0]] = [pair[1]]

  @classmethod
  def graph_density(self, v, e):
    """
    Graph denisity from vertices and edges
    en.wikipedia.org/wiki/Dense_graph
    """
    return 2 * len(e) / float(len(v) * (len(v) - 1))

  @classmethod
  def graph_stats(self, G, create_plot=False):
    mi = ma = 0
    lengths = []
    print 'nodes: {}'.format(len(G.keys()))
    for k in G.keys():
      l = len(G[k])
      # print 'key: {} adjecencylist: {}'.format(k, G[k])

      lengths.append(l)
      if l > ma: ma = l
      if l < mi or mi == 0: mi = l

    avg_length = 0
    if len(G.keys()) > 0:
      avg_length = sum(lengths) / float(len(G.keys()))

    s = 'graph adjacency list length stats: min: '+str(mi)+' max: '+str(ma)+' avg_length: '+str(avg_length) + ' number:'+str(len(G))
    print s

    if(create_plot):
      fig = plt.figure()
      fig.text(0, 0, s)
      sub = fig.add_subplot(111)
      sub.hist(lengths, bins=10, color='g')
      plt.xlabel('adjencency list length')
      plt.ylabel('occ')
      fig.savefig('../tmp/plots/graph_stats_'+str(time()).replace('.','')+'.png')

  @classmethod
  def filter_items(self, M):
    singletons = {}
    pairs = {}
    triples = {}
    G = {} # TODO: look at this graph. does it have long adjacency lists? 

    # build data structures
    for itemset, (support,) in M:
      l = len(itemset)
      if l == 1:
        singletons[itemset[0]] = support
      elif l == 2:
        sorted_pair = itemset[0] < itemset[1] and itemset or (itemset[1], itemset[0])
        pairs[sorted_pair] = support
        self.__add_to_graph(sorted_pair, G)
      elif l == 3:
        triples[utils.triple_sort(itemset)] = support
      else:
        assert False, "frequent itemsets larger than 3 are not used"
    
    # graph_stats(G)

    # print 'singletons found: {}'.format(len(singletons))
    # print 'pairs found: {}'.format(len(pairs))
    # print 'triples found: {}'.format(len(triples))
    res = []

    # find triangles in graph
    for n1 in G.keys():
      # assert singletons.has_key(n1), ("Pair cannot have infrequent singleton item", n1, sigletons)

      for n2 in G[n1]:
        # assert singletons.has_key(n2), ("Pair cannot have infrequent singleton item", n2, sigletons)
        
        # n2 does not necessarily have an adjencency list
        if not G.has_key(n2): 
          continue

        for n3 in G[n2]:
          # assert singletons.has_key(n3), ("Pair cannot have infrequent singleton item", n3, sigletons)
          
          if n3 in G[n1]: # triangle
            
            s1 = (n1, singletons[n1])
            s2 = (n2, singletons[n2])
            s3 = (n3, singletons[n3])
            s12 = ((n1,n2), pairs[(n1,n2)])
            s23 = ((n2,n3), pairs[(n2,n3)])
            s13 = ((n1,n3), pairs[(n1,n3)])

            c = 0
            if triples.has_key((n1,n2,n3)):
              c = triples[(n1,n2,n3)]

            s123 = ((n1,n2,n3), c)

            res.append((s1,s2,s3,s12,s23,s13,s123))

    # print 'Triangles found: {}'.format(len(res))
    return res, triples

  @classmethod 
  def load_and_filter(self, input_path):
    """
    Load frequent itemsets saved at the input_path, being 
    a pickle dump of the output of running frequent itemset
    mining with Bergholts mining algorithms.
    return: list of tuples of itemsets with existence of 
    pairs ab, bc, ac
    """
    M = None
    try:
      with open(input_path, 'r') as fd:
        M = pickle.load(fd)
    except:
      print "unable to load file"
      return
    return self.filter_items(M)

  # res = load_and_filter(input_path)
  # print res

  # test
  # def test():
  #   # simple triangle
  #   M1 = [
  #     ((1,),(1,)),
  #     ((2,),(1,)),
  #     ((3,),(1,)),
  #     ((1,2),(1,)),
  #     ((2,3),(1,)),
  #     ((1,3),(1,)),
  #     ((1,2,3),(1,))
  #   ]

  #   # simple not sorted
  #   M2 = [
  #     ((1,),(1,)),
  #     ((2,),(1,)),
  #     ((3,),(1,)),
  #     ((1,2),(1,)),
  #     ((3,2),(1,)),
  #     ((1,3),(1,)),
  #     ((1,2,3),(1,))
  #   ]

  #   # extra edge
  #   M3 = [
  #     ((1,),(1,)),
  #     ((2,),(1,)),
  #     ((3,),(1,)),
  #     ((4,),(1,)),
  #     ((2,1),(1,)),
  #     ((3,2),(1,)),
  #     ((3,1),(1,)),
  #     ((1,4),(1,))
  #   ]

  #   # missing pair
  #   M4 = [
  #     ((1,),(1,)),
  #     ((2,),(1,)),
  #     ((3,),(1,)),
  #     ((4,),(1,)),
  #     ((2,1),(1,)),
  #     ((3,1),(1,)),
  #     ((1,4),(1,))
  #   ]

  #   res, triples = filter_items(M1)
  #   assert len(res) == 1, res
  #   res, triples = filter_items(M2)
  #   assert len(res) == 1, res
  #   res, triples = filter_items(M3)
  #   assert len(res) == 1, res
  #   res, triples = filter_items(M4)
  #   assert len(res) == 0, res
  # # test()
# def test_node_iterator():
#     # sorted_nodes = pickle.load(open('sorted_nodes.list', 'r'))

#     transactions = CSVParser.parse_csv_to_mat('/Users/ahkj/Dropbox/SAAS/data/csv/sample-big/customers.txt')
#     all_frequent_items = fpgrowth(transactions, supp=-10, min=1, max=3)

#     print 'running'
#     times = []
#     for i in range(1000):
#         start = time()
#         triangles, triples = NodeIterator.filter_items(all_frequent_items)
#         times.append(time() - start)
#     print 'node iterator avg: {}'.format(sum(times) / float(len(times)))
#     print "Length: {}".format(len(triangles))

    # example result
    # node iterator avg: 0.0365535356998
    # Length: 3437

