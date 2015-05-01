import utils
from time import time

# TODO: clean up

def print_stats(G):
    edge_list_lengths = []
    _max = 0
    _min = 9999999
    for key in G:
        l = len(G[key][0])
        if l < _min:
            _min = l
        if l > _max:
            _max = l
        edge_list_lengths.append(l)
    
    avg = sum(edge_list_lengths) / float(len(edge_list_lengths))
    s = "Edge list max:{} min:{} avg:{} number:{}".format(_max, _min, avg, len(G))
    print s

def triangles(a, b, G):
    centers = set()
    # triangles, if b is in a's candidate dict, a 
    # triangle node exist for each center node
    if b in G[a][1]: 
        centers = G[a][1][b]

    res = []
    # Constructing the triangles, should only be a small to constant number of iterations.
    # and could entirely be omitted by returning a less pretty result og (a,b, [centers])
    for center in centers:
         # res.append(utils.triple_sort((a, center, b))) #sorted
         res.append((a, b, center)) #unsorted
    return centers, res


def insert(a, b, G, centers=set()):
    """
    Insert a, and compare b to all nodes in a's edge list 'c_i'
    insert max(b, c_i) into min(b, c_i)'s candidate dict.
    """
    # TODO, can we avoid checking the center nodes this way?
    # c is the center node of a triangle created from 
    # the edge insertion, no need for update
    for c in G[a][0]:
        if c in centers: 
            continue
        # Insert/create candidate dict on smallest Node
        if c < b:
            if b in G[c][1]:
                G[c][1][b].add(a)
            else:
                G[c][1][b] = set([a])
        else:
            if c in G[b][1]:
                G[b][1][c].add(a)
            else:
                G[b][1][c] = set([a])
    # add b to a's edge list
    G[a][0].append(b)


def fun(V, E):
    """
    Finds all triangles in the edge list.
    Nodes are unique integers. Each node is stored by its integer key in the constructed grapg G
    Edges are tuples of Nodes (intergers) (a, b).
    with a tuple ([], {}) of edge list, candidate dictionary.
    Iterative algorithm that constructs a graph, and finds
    triangles at the same time. If an end node 'a' of an inserted edge (a,b)
    is already in the graph, all neighbours c of 'a' will be compared with b,
    and the smaller will save a candidate dict with key being the min node, and the value being the set
    of middle nodes, e.g. {min(b,c_i): set(a_i)}.
    If both ends (a,b) of an edge already exists in the graph, getting all
    triangles that the edge produces is a lookup in this candidate dict, with 
    a small iteration building the triangles.
    """

    G = {}
    res = []
    for a, b in E:

        # Create non-atatched
        if not a in G and not b in G:
           G[a] = ([b], {}) 
           G[b] = ([a], {}) 

        # insert edge end 'a'
        elif a in G and not b in G:
            G[b] = ([a], {}) 
            insert(a, b, G)

        # insert edge end 'b'
        elif b in G and not a in G:
            G[a] = ([b], {})
            insert(b, a, G)

        # possible triangle
        else:
            centers = []
            ts = []
            if a < b:
                centers, ts = triangles(a, b, G)
                insert(a, b, G, centers)
                insert(b, a, G, centers)
            else:
                centers, ts = triangles(b, a, G)
                insert(a, b, G, centers)
                insert(b, a, G, centers)

            # append the result
            if len(ts) > 0:
                res = res + ts
    
    # print_stats(G)

    return res




# test_edge_iterator()



# def test():
#     edges = [(1,2), (2,3), (1,4), (4,3), (1,3)]
#     print fun(None, edges)


# def test2():

#     # mine frequent items
#     transactions = parser.parse_csv_to_mat('/Users/ahkj/Dropbox/SAAS/data/csv/sample-big/customers.txt')
#     all_frequent_items = fpgrowth(transactions, supp=-10, min=1, max=3)

#     # edges
#     edges = [items for (items, freq) in all_frequent_items if len(items) == 2]
#     print 'mined edges'

#     # Time the 'fun' algorithm
#     times = []
#     for i in range(1000):
#         start = time()
#         triangles = fun(None, edges)
#         times.append(time() - start)
#     print 'fun avg: {}'.format(sum(times) / float(len(times)))
#     print "Length: {}".format(len(triangles))

#     # Time the filter items algorithm
#     times = []
#     for i in range(1000):
#         start = time()
#         triangles, trips = filter_items(all_frequent_items)
#         times.append(time() - start)
#     print 'filter avg: {}'.format(sum(times) / float(len(times)))
#     print "Length: {}".format(len(triangles))
# test2()


