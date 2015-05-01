from sys import argv
from fim import fpgrowth
import pickle

import parser

input_path = argv[1]
output_path = len(argv)>2 and argv[2] or '../var/frequent_itemsets.out'

def write_frequent_itemsets(input_path, output_path, support=-10, min_set_size=1, max_set_size=3):
  # parse transactions from file
  transactions = parser.parse_csv_to_mat(input_path)
  
  # mine frequent itemsets
  frequent_itemsets = fpgrowth(transactions, supp=support, min=min_set_size, max=max_set_size)
  
  # write result to file
  with open(output_path, 'w+') as fd:
    pickle.dump(frequent_itemsets, fd)

write_frequent_itemsets(input_path, output_path)

# test load file
# fd = open(output_path, 'r')
# M = pickle.load(fd)
# fd.close()

# print M