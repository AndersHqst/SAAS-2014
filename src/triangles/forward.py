
from parsers import CSVParser
from utils import triple_sort
from utils import mem_size
from time import time
import sys


class Forward():

    @classmethod
    def __add_to_nodes(self, V, a, b, keys):
        """
        Add an edge (a, b) as nodes and to
        eachoters adjecency lists.
        And, add nodes to list of keys if not already
        in the nodes.
        """
        if a in V:
            V[a].append(b)
        else:
            V[a] = [b]
            keys.append(a)
        if b in V:
            V[b].append(a)
        else:
            V[b] = [a]
            keys.append(b)


    @classmethod
    def forward(self, frequent_items):
        """
        Run the forward algorithm for finding
        triangles.
        """
        keys = []
        singletons = {}
        pairs = {}
        triples = {}
        V = {}

        # build data structures
        for itemset, (support,) in frequent_items:
            l = len(itemset)
            if l == 1:
                singletons[itemset[0]] = support
            elif l == 2:
                a, b = itemset[0], itemset[1]
                sorted_pair = a < b and itemset or (b, a)
                pairs[sorted_pair] = support
                self.__add_to_nodes(V, a, b, keys)
            elif l == 3:
                triples[triple_sort(itemset)] = support
            else:
                assert False, "frequent itemsets larger than 3 are not used"

        # print 'Forward space usage in mb:'
        # print 'keys: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # print 'singletons: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # print 'pairs: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # print 'triples: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # This is wrong, needs to traverse the graph
        # print 'V : ', mem_size.bytes_to_mb(sys.getsizeof(V))


        # Keys have to be sorted for running Forward
        keys.sort()

        res = []
        A = {}
        for key in keys:
            A[key] = set()
        for s in keys:
            adj = V[s]
            for t in adj:
                if s < t:
                    for v in A[s]:
                        if v in A[t]:
                            n1, n2, n3 = triple_sort((v, s, t))
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

                    A[t].add(s)
        # print 'A', mem_size.bytes_to_mb(sys.getsizeof(A))
        # print 'res', mem_size.bytes_to_mb(sys.getsizeof(res))
        # print 'triangles found: ', len(res)

        return res, triples


    @classmethod
    def graph_size(self, V):
        bytes_ = 0
        bytes_ += sys.getsizeof(V.keys())
        for l in V.values():
            bytes_ += sys.getsizeof(l)
        print 'graph size: ', mem_size.bytes_to_mb(bytes_)

    @classmethod
    def triplets_size(self, triplets):
        bytes_ = 0
        for a, adj in triplets:
            bytes_ += sys.getsizeof(a)
            bytes_ += sys.getsizeof(adj.keys())
            for b in adj.keys():
                bytes_ += sys.getsizeof(b)
                bytes_ += sys.getsizeof(adj[b].values())
        print 'triplets size: ', mem_size.bytes_to_mb(bytes_)


    @classmethod
    def forward_compact(self, frequent_items_file, min_support, observed, only_interesting_triples, restricted_triples):
        """
        Run the forward algorithm for finding
        triangles.
        Found triangles are stored as a (compact) tree 
        """
        keys = []
        singletons = {}
        pairs = {}
        triples = {}
        V = {}

        # build data structures
        for index, line in enumerate(open(frequent_items_file, 'rb')):
            # if index % 1000000 == 0:
            #     print 'Building ds. lines read: ', index
            #     print 'singletons size: ', mem_size.bytes_to_mb(sys.getsizeof(singletons))
            #     print 'pairs size: ', mem_size.bytes_to_mb(sys.getsizeof(pairs))
            #    # print 'triples size: ', mem_size.bytes_to_mb(Forward.triplets_size(triples))
            #     print 'keys size: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
            #     Forward.graph_size(V)

            chunks = line.split() # ex: a b c (42)
            itemset = tuple(chunks[:-1])
            support = int(chunks[-1].replace('(', '').replace(')', ''))

            # Build graph to be searched for triangles, and save
            # itemssets to dicts so we can easily look up there support
            # in forward when triangles are found.
            l = len(itemset)
            if l == 1:
                singletons[itemset[0]] = support
            elif l == 2:
                a, b = itemset[0], itemset[1]
                sorted_pair = a < b and itemset or (b, a)
                pairs[sorted_pair] = support # Store this support in the graph?
                self.__add_to_nodes(V, a, b, keys)
            elif l == 3:
                a, b, c = triple_sort(itemset)
                if not a in triples:
                    triples[a] = {b: {c: support}}
                else:
                    a_dict = triples[a]        
                    if not b in a_dict:
                        a_dict[b] = {c: support}
                    else:
                        b_dict = a_dict[b]
                        b_dict[c] = support
                #triples[] = support
            else:
                assert False, "frequent itemsets larger than 3 are not used"
        # print 'Done building ds'
        # print 'Forward space usage in mb:'
        # print 'keys: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # print 'singletons: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # print 'pairs: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # print 'triples: ', mem_size.bytes_to_mb(sys.getsizeof(keys))
        # This is wrong, needs to traverse the graph
        # print 'V : ', mem_size.bytes_to_mb(sys.getsizeof(V))


        # Keys have to be sorted for running Forward
        keys.sort()
        # print 'keys sorted. keys: ', len(keys)

        res = {}
        A = {}
        for key in keys:
            A[key] = set()
        for index, s in enumerate(keys):
            adj = V[s]
            # if index % 10000 == 0:
            #     print 'key index: ', index
            #     print 'pct done: ', (index / float(len(keys)))
            #     print 'cache size: ', Forward.graph_size(A)
            #     print 'longest cache list'
            #     max_ = -1
            #     sum_ = 0
            #     for l in A: 
            #         length = len(l)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            #         if length > max_:
            #             max_ = length
            #         sum_ += length                                                                                                                                                                                                                                                                                                                                                              
            #     print max_
            #     lists = float(len(A))
            #     print 'avg length: ', (sum_ / lists)
            #     print 'lists', lists
            for t in adj:
                # if index > 40000 and index % 500 == 0:
                #     print 'adj len: ', len(adj)
                if s < t:
                    for v in A[s]:
                        # if index > 40000 and index % 500 == 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       :
                        #     print 'A[s] len: ', len(A[s])
                        if v in A[t]:
                            n1, n2, n3 = triple_sort((v, s, t))

                            # get triple support
                            triple_support = 0
                            try:
                                triple_support = triples[n1][n2][n3]
                            except KeyError as ke:
                                pass

                            # check if this is a triple has sufficient support
                            # in the observed data
                            observed_triples = 0
                            if (n1, n2, n3) in observed:
                                observed_triples = observed[(n1, n2, n3)] - triple_support
                            if observed_triples < min_support:
                                continue

                            if only_interesting_triples and triple_support != 0:
                                continue

                            if not restricted_triples is None and not (n1, n2, n3) in restricted_triples:
                                continue

                            # At this point this is a triangle/triple to be estimate.
                            # Triangles are held in a tree ds, with no root node,
                            # and sorted nodes to reuse singletons and pairs
                            # that occur more than once.
                            if not n1 in res:
                                res[n1] = (singletons[n1], {})

                            n1_dict = res[n1][1]
                            
                            if not n2 in n1_dict:
                                n1_dict[n2] = (singletons[n2], pairs[(n1,n2)], {})

                            n2_dict = n1_dict[n2][2]
                            
                            if not n3 in n2_dict:
                                n2_dict[n3] = (singletons[n3], pairs[(n1, n3)], pairs[(n2, n3)], triple_support)
                            else:
                                assert False, 'Triplets can only be found once!'

                    A[t].add(s)
        # print 'A', mem_size.bytes_to_mb(sys.getsizeof(A))
        # This is wrong, needs to traverse the graph
        # print 'res', mem_size.bytes_to_mb(sys.getsizeof(res))
        print 'forward done'
        t_count = 0
        for k in res.keys():
           d2 = res[k][1]
           for k2 in d2.keys():
               t_count += len(d2[k2][2].keys())
        print 'triangles found :', t_count
        return res, triples

# def test_forward():
#from fim import fpgrowth
#     # sorted_nodes = pickle.load(open('sorted_nodes.list', 'r'))

#     transactions = CSVParser.parse_csv_to_mat('/Users/ahkj/Dropbox/SAAS/data/csv/sample-big/customers.txt')
#     all_frequent_items = fpgrowth(transactions, supp=-5, min=1, max=3)

#     print 'running'
#     times = []
#     for i in range(100):
#         start = time()
#         triangles, triples = Forward.forward_compact(all_frequent_items)
#         times.append(time() - start)
#     print 'forward avg: {}'.format(sum(times) / float(len(times)))
#     print "Length: {}".format(len(triangles))

# test_forward()
