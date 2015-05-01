import gc
import random 
from math import log

# Align plot text
PLOT_TEXT_Y = -0.05
PLOT_TEXT_X = 0.12

def avg(arr):
    return sum(arr) / float(len(arr))
    
def interpolate(averages):
    for index, val in enumerate(averages):
        if val == 0 and index > 0:
            averages[index] = averages[index-1]

def chunks(l, n):
    """ 
    Yield successive n-sized chunks from l, chunk-index, and l minus the chunk
    return: (chunk, chunk_index, l/chunk)
    """
    for i, c in enumerate(xrange(0, len(l), n)):
        yield l[c:c+n], i, l[0:c]+l[c+n:len(l)]


def confidence_interval(errors):
    # tvar is the sample variance
    from scipy.stats import norm, tvar
    import math

    mu = sum(errors) / float(len(errors))
    var = tvar(errors)
    std_dev = math.sqrt(var)
    std_error = std_dev / math.sqrt(len(errors))
    span_95 = norm.interval(0.95, loc=mu, scale=std_error)

    return span_95


def triple_sort(tup):
    """
    Sort a triple in ascending order
    """
    a, b, c = tup
    if a < b:
        if b < c:
            return tup
        elif a < c:
            return (a, c, b)
        return (c, a, b)
    elif a < c:
        return (b, a, c)
    elif c < b:
        return (c, b, a)
    return (b, c, a)


def information(prob, trials):
    ent = 0
    for i in range(trials):
        ent += log(prob,2)*prob
    return -1 * ent


def generate_random_data(lines, items, in_mem=True, max_trans_length=3, output_file=None):
    """
    Generate a random data file, of non empty transaction, 
    that can be read by Borgelts algorithms. 
    Dublicate items in a transaction are possible.
    Returns a matrix (jagged lists) of the data.
    """
    # output file
    if not output_file is None:
        fd = open(output_file, 'w')

    # matrix (with zero rows)
    m = []

    # write lines of random transactions
    gc.disable()
    for line in range(lines):

        # number of transactions in this line is [1, max_trans_length]
        transaction_length = random.randrange(1, max_trans_length+1)

        trans = []
        for i in range(transaction_length):
            trans.append(random.randint(0, items))
        if in_mem:
            m.append(trans)

        # convert int array to string, ended with newline, and write to file
        if not output_file is None:
            fd.write(' '.join([str(i) for i in trans]) + '\n')

    # clean up
    gc.enable()
    if not output_file is None:
        fd.close()

    return m

def phi(x,y):
    import math
    """
    Calculates the pearson phi coefficient for 
    two binary vectors
    http://en.wikipedia.org/wiki/Phi_coefficient
    """
    assert len(x) == len(y)

    ns = [0,0,0,0]
    for x_i, y_i in zip(x, y):
        ns[x_i << 1 | y_i] += 1
    assert sum(ns) == len(x)

    n1_ = ns[3] + ns[2]
    n0_ = ns[1] + ns[0]
    n_1 = ns[3] + ns[1]
    n_0 = ns[2] + ns[0]

    rooted_sums = math.sqrt(n1_ * n0_ * n_1 * n_0)
    if rooted_sums == 0:
        rooted_sums = 1

    return (ns[3] * ns[0] - ns[2] * ns[1]) / rooted_sums


def clean_tsv_for_zero_estimates(infile, outfile):
    """
    Use this to clean a file with estimates for 
    0 estiamtes. Eg extrapolation can often yield this
    and removing the 0's makes plotting easier.
    """
    fd = open(infile, 'rb')
    clean_file = open(outfile, 'w')
    zero_lines = 0
    for index, line in enumerate(fd.readlines()):
        if index == 0:
            clean_file.write(line)
        else:
            chunks = line.split('\t')
            est = float(chunks[0])
            if est < 1:
                zero_lines += 1
            else:
                clean_file.write(line)
    fd.close()
    clean_file.close()
    print 'Done cleaning tsv file. Removed {} zeroes.'.format(zero_lines)

def clean_extrapolation_files(folder):
    import os
    """
    Iterates all extrapolation files from a CV output
    and puts zero estiamtes in to a 'cleaned' file.
    """
    iteration = 0
    while True:
        ext_est_file = folder + str(iteration) + '_data_extrapolation.tsv'
        
        if not os.path.exists(ext_est_file):
            break

        # Cleaned file name
        ext_est_cleaned_file = folder + str(iteration) + '_data_extrapolation_cleaned.tsv'

        # Clean
        clean_tsv_for_zero_estimates(ext_est_file, ext_est_cleaned_file)

        iteration += 1

def mid_inter_quantile(arr):
    t1_quantile = int(len(arr) * 0.25)
    t3_quantile = int(len(arr) * 0.75)
    return arr[t1_quantile, t3_quantile]

def create_zero_trip_files(folder):
    import os
    from parsers import CVOutputParser
    """
    Iterate .tsv file and only write estimates where the triple was 0 in the sample
    to another file.
    """
    iteration = 0
    while True:
        max_ent_file = folder + str(iteration) + '_data.tsv'
        
        if not os.path.exists(max_ent_file):
            break

        # Cleaned file name
        max_ent_zero_trips_file = folder + str(iteration) + '_data_zero_trips.tsv'
        fd = open(max_ent_zero_trips_file, 'w')

        # write header
        fd.write('est\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')

        # Clean
        for (n1, n2, n3), (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version_2(max_ent_file):

            s1, s2, s3, s12, s13, s23, s123 = triangle

            if s123 != 0:
                continue

            fd.write(str(est) + '\t' + str(obs) + '\t' + str(n1) + '\t' + str(n2) + '\t' + str(n3) + '\t' + str(ratio) + '\t' + str(s1) + '\t' + str(s2) + '\t' + str(s3) + '\t' + str(s12) + '\t' + str(s13) + '\t' + str(s23) + '\t' + str(s123) + '\n')

        fd.close()

        iteration += 1

def merge_sample(folder):
    import os
    from parsers import CVOutputParser
    """
    Creates a single a single .tsv file with maxent and extrapolation
    results.
    """

    iteration = 0
    maxent_estimates = []
    while True:
        max_ent_file = folder + str(iteration) + '_data.tsv'
        
        if not os.path.exists(max_ent_file):
            break

        for (n1, n2, n3), (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version_2(max_ent_file):
            s1, s2, s3, s12, s13, s23, s123 = triangle
            maxent_estimates.append(est)
        iteration += 1
        print 'iteration ', iteration


    # merged file name
    merged_file = folder + 'merged_estimates.tsv'
    fd = open(merged_file, 'wr')
    # write header
    fd.write('est\text\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')

    iteration = 0
    estimate_number = 0
    while True:
        ext_file = folder + str(iteration) + '_data_extrapolation.tsv'
        
        if not os.path.exists(ext_file):
            break

        for (n1, n2, n3), (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version_2(ext_file):
            s1, s2, s3, s12, s13, s23, s123 = triangle
            fd.write(str(maxent_estimates[estimate_number]) + '\t' + str(est) + '\t' + str(obs) + '\t' + str(n1) + '\t' + str(n2) + '\t' + str(n3) + '\t' + str(ratio) + '\t' + str(s1) + '\t' + str(s2) + '\t' + str(s3) + '\t' + str(s12) + '\t' + str(s13) + '\t' + str(s23) + '\t' + str(s123) + '\n')
            estimate_number += 1

        iteration += 1
        print 'iteration ', iteration
    fd.close()
    print 'merging files done'


# def confidence_interval():
    # in some sample, we calculate the % errors.
    # This gives some distribution
    # calculate errors as a percentage, currently absolute errors
    # have the issue of big estimates weigh too much
    # cross validate max ent estimate on som subset of triplets
    # how good/bad is this estiamte? Confidence interval,
    # ie with 95% percent change our error mean is only x std. from true
    # error mean.

    # Can this confidence tell us anything about how well a sample will work
    # ie how good estiamtes are?

    # Could we calcualte this for both max_ent and extrapolation and 
    # find some threshold there?

    # Varianse in the data. The distribution of the sample has some variance
    # ie frequnecy on item counts, can this be related to the error?



# def test_triple_sort():
#     res = (1, 2, 3)
#     assert triple_sort((1, 2, 3)) == res
#     assert triple_sort((1, 3, 2)) == res
#     assert triple_sort((2, 1, 3)) == res
#     assert triple_sort((2, 3, 1)) == res, triple_sort((2, 3, 1))
#     assert triple_sort((3, 2, 1)) == res
#     assert triple_sort((3, 1, 2)) == res

#     res = (1,1,3)
#     assert triple_sort((1, 1, 3)) == res
#     assert triple_sort((1, 3, 1)) == res
#     assert triple_sort((1, 1, 3)) == res
#     assert triple_sort((1, 3, 1)) == res
#     assert triple_sort((3, 1, 1)) == res
#     assert triple_sort((3, 1, 1)) == res

# def test_chunks():
#     l = [1,2,3,4,5,6]
#     i=0
#     for chunk, index, rest in chunks(l, 2):
#         assert len(chunk) == 2, (chunk, rest)
#         assert not chunk in rest, (chunk, rest)
#         assert index == i, (index, i)
#         i += 1

#     l = [1,2,3,4,5]
#     i = 0
#     for chunk, index, rest in chunks(l, 2):
#         assert len(chunk) <= 2, (chunk, rest)
#         assert not chunk in rest, (chunk, rest)
#         assert index == i, (index, i)
#         i += 1

#     l = [1,2,3,4,5]
#     i = 0
#     for chunk, index, rest in chunks(l, 3):
#         assert len(chunk) <= 3, (chunk, rest)
#         assert not chunk in rest, (chunk, rest)
#         assert index == i, (index, i)
#         i += 1

# test_chunks()