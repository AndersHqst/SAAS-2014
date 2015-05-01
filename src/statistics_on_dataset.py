import sys


def stats_on_dataset(name_of_file):

    Length = 0
    Transactions=0
    longest_trans=0
    longest_trans_string=''
    uniqueness=set()
    total_items_in_all_transactions=0

    
    for line in open(name_of_file, 'r'):
        #Below is for untrimmed data.
        #words = line.split('\t')[1].split(' ')

        #Below is for trimmed data file
        words = line.split(' ')

        Transactions+=1
        Length=Length+len(words)
        if longest_trans < len(words):
            longest_trans=len(words)
            longest_trans_string=words
        #words_string=''.join(words)
        for i in words:
            #total_items_in_all_transactions=total_items_in_all_transactions+1
            uniqueness.add(i)


    print('number of transactions / itemsets:')
    print(Transactions)
    print('total amount of items in all transactions:')
    print(Length)
    print('Average number of items in each transactions / itemset:')
    print(float(Length)/float(Transactions))
    print('The longest itemset contains:')
    print(longest_trans)
    print('The amount of unique items is:')
    print(len(uniqueness))
    print('The average amount of unique items per transactions:')
    print(float(len(uniqueness))/float(Transactions))
    print('finally the amount of items per unique item:')
    print(float(Length)/len(uniqueness))


#check cuckoo hashing