class MovieLensParser:

    @classmethod
    def __parse_data(self, fd):
        transactions = []
        for line in fd.readlines():
            # Ignore first 'user id' value
            transaction = line.split()[1:]
            transactions.append(transaction)
        return transactions


    @classmethod
    def parse_movie_lens_to_mat_small(self, path):
        """
        Parse and get the transactions from the MovieLens 
        data set.
        """
        with open(path, 'rb', path) as fd:
            return self.__parse_data(fd)

    @classmethod
    def parse_movie_lens_to_mat_medium(self):
        """
        Parse and get the transactions from the MovieLens 
        data set.
        """
        with open(path, 'rb') as fd:
            return self.__parse_data(fd)

    @classmethod
    def parse_movie_lens_to_mat_large(self, path):
        """
        Parse and get the transactions from the MovieLens 
        data set
        """
        with open(path, 'rb') as fd:
            return self.__parse_data(fd)


