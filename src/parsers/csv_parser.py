import gc

class CSVParser():

    @classmethod
    def parse_csv_to_mat(self, path, sep=' '):
        """
        parse csv style file to matrix (list of lists)
        and make statistic on input file.
        """

        fd = open(path, 'r')        
        number_of_trans=0
        
        max_len = -sys.maxint - 1
        min_len = sys.maxint
        acumulated_trans_length = 0
        temp_trans_len = 0

        for line in fd.readlines():
            num_of_trans+=1
        unique_items = {}
        

        transactions = []

        for line in fd.readlines():
            temp_trans = line.split(sep)
            temp_trans_len = temp_trans.len()
            acumulated_trans_length= temp_trans_len + acumulated_trans_length
            if temp_trans_len > max_len:
                max_len = temp_trans_length
            if temp_trans_len() < min_len:
                min_len = temp_trans_len
            temp_trans
            num_of_trans+=1
            transactions.append([i for i in temp_trans])
            for i in temp_trans:
                if not unique_items.has_key(i):
                    unique_items[i] = 1
        
        fd.close()
        gc.enable() # enable garbage collector
        #stat_file = '../tmp/stats_' +  + '/'
        print 'Number of total transactions: ' , num_of_trans 
        print 'Minimum length: ', min_len
        print 'Maximum length: ' , max_len
        average_len = acumulated_trans_length/float(num_of_trans)
        print 'Average length: ' ,  average_len
        print 'Number of unique items: ' , unique_items

        return transactions 
        