from utils import triple_sort

class Preprocessor():
    @classmethod
    def triple_intervals(self, frequent_items_file, intervals):
        """
        The funktion runs through a frequent items file produced by fp-growth.
        and filter the triplets out and sorts the triplets by frequncy.
        Finaly it devides the frequent itemsets into intervals 
        of the triplets with a specific frequency range.
        """

        triples = []
        frequencies = set()
        for line in open(frequent_items_file, 'rb'):
            chunks = line.split()
            if len(chunks) < 4:
                continue
            itemset = tuple(chunks[:-1])
            support = int(chunks[-1].replace('(','').replace(')',''))
            frequencies.add(support)
            triples.append((itemset, support))
        triples.sort(lambda x,y: x[1]< y[1] and -1 or 1)
        frequencies_sorted = list(frequencies)
        frequencies_sorted.sort()

        # print 'frequencies_sorted: {}'.format(len(frequencies_sorted))
        # print 'triples: ', len(triples)

        result = []
        chunk_intervals = [] 
        interval = len(frequencies_sorted) / intervals
        triple_index = 0
        for c in xrange(0, len(frequencies_sorted), interval):
            triple_set = {} # subset of triples, with given frequency
            chunk = frequencies_sorted[c:c+interval] # Chunk of frequencies
            chunk_intervals.append((chunk[0], chunk[-1]))
            for freq in chunk:
                triple, support = triples[triple_index]
                while support == freq:
                    triple_set[triple_sort(triple)] = support
                    triple_index += 1
                    if triple_index < len(triples):
                        triple, support = triples[triple_index]
                    else:
                        break
            result.append(triple_set)

        set_lengths = [len(l) for l in result]
        print "Set sizes: {}".format(set_lengths)
        print "Intervals: {}".format(chunk_intervals)
        return result
