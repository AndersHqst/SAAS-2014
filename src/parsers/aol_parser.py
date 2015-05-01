# import gc
import os
class AOLParser():

    @classmethod
    # Running on all 10 files gives 15.378.227 dublicates
    # and results in a single 365M file (due to trimmed data and dublicates)
    # 14G 21 Mar 01:47 frequent_items_aol_supp_100.tab
    def parse_aol_to_mat(self, path, merged_file='../tmp/all_aol.tab', num_files=10):
        """
        parse AOL style file to matrix (list of lists)
        """

        # Get paths to all AOL colection files.
        input_paths = []
        for i in range(num_files):
            prefix = i < 9 and '0' or ''
            filename = path + 'user-ct-test-collection-' + prefix + '%d.txt' % (i+1)

            if not os.path.exists(filename):
                print "AOL file at path: {} does not exist. Root path {}".format(filename, path)
                return

            print 'AOL adding file path: ', path
            input_paths.append(filename)

        # Parse files
        # gc.disable() # disable garbage colection
        transactions = []
        dublicate_count = 0
        out = open(merged_file, 'w') 

        for path in input_paths: # the aol-dataset distributed over 10 files.
            fd =  open(path, 'r')  
             
            # the two variables previous_searchs_content and  previous_user is used to check if it is the same search.
            # if this is the case, the search content should not be stored as a new transaction. 
            previous_searchs_content = None 
            previous_user = None
            for line in fd.readlines():
                temp_line_array = line.split('\t')
                this_user = temp_line_array[0]
                this_searchs_content = temp_line_array[1]
                if previous_searchs_content != this_searchs_content or previous_user!= this_user :
                    #transactions.append(' '.join(this_searchs_content.split()))
                    out.write(' '.join(this_searchs_content.split()) + '\n')
                    previous_searchs_content = this_searchs_content
                    previous_user = this_user
                else:
                    dublicate_count += 1

            fd.close()
        out.close()
        # gc.enable() # enable garbage collection

        print 'AOL parser parsed {} transactions'.format(len(transactions))
        print 'Dublicates: ', dublicate_count
        #return transactions

# AOLParser.parse_aol_to_mat('../../../data/infochimps_aol-search-data/AOL-user-ct-collection/','../../tmp/all_aol.tab')