from utils import triple_sort
def build_item_search_tree(tsvfile):
    """
    Returns a tree data structure that
    can be used with the look up function.
    """
    s1_pos = s2_pos = s3_pos = est_pos = None
    ds = {}
    for index, line in enumerate(open(tsvfile)):
        line = line.replace('\n', '')
        chunks = line.split('\t')
        if index == 0:
            s1_pos = chunks.index('n1')
            s2_pos = chunks.index('n2')
            s3_pos = chunks.index('n3')
            est_pos = chunks.index('est')
        else:
            s1, s2, s3, est = chunks[s1_pos], chunks[s2_pos], chunks[s3_pos], float(chunks[est_pos])
            # We expect items to be sorted, but just in case
            s1, s2, s3 = triple_sort((s1, s2, s3))
            if (s1, s2) in ds:
                ds[(s1, s2)].append((s3, est))
            else:
                ds[(s1, s2)] = [(s3, est)]
            if (s1, s3) in ds:
                ds[(s1, s3)].append((s2, est))
            else:
                ds[(s1, s3)] = [(s2, est)]
            if (s2, s3) in ds:
                ds[(s2, s3)].append((s1, est))
            else:
                ds[(s2, s3)] = [(s1, est)]
    return ds

def lookup(a, b, ds, results=10):
    """
    Lookup items a, b and get highest estimated
    results.
    """
    a, b = a < b and (a, b) or (b, a)
    if (a, b) in ds:
        ests = ds[(a, b)]
        # descending sort on the estimate value in the tuples
        ests.sort(lambda x,y : x[1] < y[1] and 1 or -1)
        return ests[:results]
    return []

ds=build_item_search_tree('../tmp/cv_139815414821_/0_data.tsv')
print lookup('in', 'the', ds) 
# result
# [('the', 747.0), ('to', 585.0), ('and', 450.0), ('a', 441.0), ('you', 432.0), ('in', 423.0), ('of', 396.0), ('i', 378.0), ('lyrics', 333.0), ('for', 315.0)]