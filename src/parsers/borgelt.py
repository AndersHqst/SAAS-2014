
class Borgelt():

    @classmethod
    def read_frequent_items(self, filename):
        """
        Reads the result file from running Borgelt's
        fpgroth, and returns a collection of
        frequent items as the would from Borgelts
        Python lib.
        """
        frequent_items = [((-1,), (-1,))]
        with open(filename, 'r') as fd:
            lines = fd.readlines()
            frequent_items = [None for i in lines]
            for index, line in enumerate(lines):
                chunks = line.split()
                items = chunks[:-1]
                count = int(chunks[-1].replace('(', '').replace(')', ''))
                frequent_items[index] = (tuple(items), (count,))
        return frequent_items