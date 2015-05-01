from fim import fpgrowth
import parser
import matplotlib.pyplot as plt

def plot_item_stats(x, y, filename):
    fig = plt.figure()
    sub = fig.add_subplot(111)
    sub.scatter(x, y)
    plt.xlabel('frequency of occurences')
    plt.ylabel('occ')
    fig.text(0, 0, x)
    fig.savefig(filename)


def item_stats():
    """
    Plot stats on frequent itemset occurences
    """
    transactions = parser.parse_csv_to_mat('/Users/ahkj/Dropbox/SAAS/data/csv/sample-big/customers.txt')
    frequent_itemsets = fpgrowth(transactions, supp=0.0005, max=3 ) 
    frequencies_1=[]
    frequencies_2 =[]
    frequencies_3 = []
    for frequent_itemset in frequent_itemsets:
	   if len(frequent_itemset[0])==1:
	       frequencies_1.append(frequent_itemset[1][0])
	   elif len(frequent_itemset[0])==2:
		   frequencies_2.append(frequent_itemset[1][0])
	   elif len(frequent_itemset[0])==3:
		   frequencies_3.append(frequent_itemset[1][0])

    frequencies_counts_1 = [0 for x in range(max(frequencies_1)+1)]
    frequencies_counts_2 = [0 for x in range(max(frequencies_2)+1)]
    frequencies_counts_3 = [0 for x in range(max(frequencies_3)+1)]

    for frequencie in frequencies_1:
        frequencies_counts_1[frequencie]+=1

    for frequencie in frequencies_2:
        frequencies_counts_2[frequencie]+=1

    for frequencie in frequencies_3:
        frequencies_counts_3[frequencie]+=1


    cleaned_ys_1 = frequencies_counts_1[0:30]
    xs_1 =[x for x in range(len(cleaned_ys_1))]
    plt.scatter(xs_1, cleaned_ys_1)
    plot_item_stats(xs_1, cleaned_ys_1, '../tmp/plots/item_stats/signletons.png')

    cleaned_ys_2 = frequencies_counts_2[0:30]
    xs_2 =[x for x in range(len(cleaned_ys_2))]
    plot_item_stats(xs_2, cleaned_ys_2, '../tmp/plots/item_stats/pairs.png')
    

    cleaned_ys_3 = frequencies_counts_3[0:30]
    xs_3 =[x for x in range(len(cleaned_ys_3))]
    plot_item_stats(xs_3, cleaned_ys_3, '../tmp/plots/item_stats/triples.png')

# item_stats()