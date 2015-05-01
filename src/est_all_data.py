from sys import argv
import os
import numpy as np
from triangles import Forward
from entropy import Entropy as ent
from utils import triple_sort
from time import time
import env
import json
import math
from scipy.stats import norm # sample variance
from numpy import var

def min_supported_trips(min_support, transactions):
    """
    Convert support argument to actual number of 
    transactions
    min_support: support as a pct, or explicity if negative
    transactions: total transactions get actual number from
    """
    min_support_trips = min_support
    # If min_support is set to a positive number (ie a pct), 
    # we convert it to an explicit number to be used in Forward
    if min_support > 0:
        min_support_trips = transactions * (min_support / 100.)
        min_support_trips = int(min_support)
    return abs(min_support_trips)
    

def est_all_data_disc_version(algorithm, tab_file, min_support=-30, iterations=1, only_interesting_triples=False, restricted_triples=None, extra_id=''):
    from subprocess import call
    from parsers import Borgelt

    cv_start = time()

    # Create work folder
    _id = str(time()).replace('.','') + '_' + extra_id
    path = '../tmp/cv_' + _id + '/'
    os.mkdir(path)
    print "\n### Running cross validation on ALL DATA cv_{}###".format(_id)

    total_transactions = 0
    for line in open(tab_file, 'rb'):
        total_transactions += 1
    print 'Total total_transactions: ', total_transactions
    sample_size = total_transactions

    avg_errors = []
    var_errors = []
    avg_errors_ext = []
    var_errors_ext = []
    avg_errors_heu = []
    var_errors_heu = []
    for index in range(iterations):

        borgelt_start = time()
        sample_freq_name = path + str(index) + '_sample_frequent_items.out'
        args = [algorithm, tab_file, sample_freq_name, '-s' + str(min_support), '-n3']
        call(args)
        print 'fpgrowth on sample data (ALL DATA) done: {} secs'.format(time()-borgelt_start)


        freq = Borgelt.read_frequent_items(sample_freq_name)
        # Create ds of all observed triplets
        # Saved as sorted keys for lookup,
        # and their frequency as value
        observed = {}
        count = 0
        for item in freq:
            if len(item[0]) == 3:
                sorted_trip = triple_sort(item[0])
                # * 2, horrible hack to make Forward calculated the 
                # observed frequency correctly.
                observed[sorted_trip] = item[1][0] * 2
        print 'Total triplets observed:', len(observed)

        # Check any frequent items were found
        if not os.path.exists(sample_freq_name):
            print 'No frequent items found'
            print 'args', args
            continue

        min_support_trips = min_supported_trips(min_support, total_transactions)
        print 'Forward min_support_trips set to: ', min_support_trips
        triangles_start = time()
        triangle_tree, sample_triples = Forward.forward_compact(sample_freq_name, min_support_trips, observed, only_interesting_triples, restricted_triples)
        print 'Found triangles done: {}'.format(time() - triangles_start)

        #del sample_freq

        estimates = []
        extrapolations = []
        heurestics = []
        observations = []
        triplets = []
        MAPE_errors = []
        MAPE_errors_ext = []
        triangle_counts = []
        triplets = []
        pair_triple_ratios = []

        # Recursion for estimate to converge
        req_depth = int(math.log(total_transactions, 2))+1

        # DFS of the tree holding all triangles
        for n1 in triangle_tree.keys():
            s1, s2_dict = triangle_tree[n1]
            for n2 in s2_dict.keys():
                s2, s12, s3_dict = s2_dict[n2]                                                                                                                                                                                                                          
                for n3 in s3_dict.keys():                                                                                                                                       
                    s3, s13, s23, s123 = s3_dict[n3]

                    triangle = (n1, n2, n3)  
                    triplets.append(triangle)

                    triangle_counts.append((s1, s2, s3, s12, s13, s23, s123))   

                    pair_triple_ratio = s123 / float(min(s12, s13, s23))
                    pair_triple_ratios.append(pair_triple_ratio)                                                                                                                                                                                                                                                                                                                                                                                                                                   

                    # Observed is the triple support, since sample is all data
                    obs = s123

                    # maxent estimate
                    est = ent.maxent_est_rosa(s1, s2, s3, s12, s23, s13, float(total_transactions), num=req_depth)

                    # extrapolation estimate, does not make sense for all data
                    est2 = s123 / float(sample_size) * (total_transactions)

                    # heurestic, use max_ent for 0 triple in sample, does not make sense for all data
                    # est3 = s123 == 0 and est or est2

                    estimates.append(est)
                    # extrapolations.append(est2)
                    # heurestics.append(est3)
                    observations.append(obs)
                    triplets.append(triangle)

                    # MAPE error max ent
                    error = abs(obs-est) / math.sqrt(obs)
                    MAPE_errors.append(error)
                    # MAPE error extrapolation
                    error2 = abs(obs-est2) / math.sqrt(obs)
                    MAPE_errors_ext.append(error2)
                    # MAPE error heurestic
                    # error3 = abs(obs-est3) / float(obs) * 100
                    # MAPE_errors_heu.append(error3)

        
        del triangle_tree
        del sample_triples
                    
        if len(MAPE_errors) > 0: #TODO handle this, probably when nothing has been found

            min_error = min(MAPE_errors)
            max_error = max(MAPE_errors)

            # max ent error
            avg_error = sum(MAPE_errors) / float(len(MAPE_errors))
            avg_errors.append(avg_error)

            # extrapolation error
            # avg_error_ext = sum(MAPE_errors_ext) / float(len(MAPE_errors_ext))
            # avg_errors_ext.append(avg_error_ext)
            
            # heurestic error
            # avg_error_heu = sum(MAPE_errors_heu) / float(len(MAPE_errors_heu))
            # avg_errors_heu.append(avg_error_heu)
            
            # variance
            var_error = var(MAPE_errors)
            # var_error_ext = tvar(MAPE_errors_ext)
            # var_error_heu = tvar(MAPE_errors_heu)

            # max_ent confidence interval
            std_dev = math.sqrt(var_error)
            std_error = std_dev / math.sqrt(sample_size)
            span_99 = norm.interval(0.99, avg_error, std_error)
            span_95 = norm.interval(0.95, avg_error, std_error)

            # ext confidence interval
            # std_dev_ext = math.sqrt(var_error_ext)
            # std_error_ext = std_dev_ext / math.sqrt(sample_size)
            # span_99_ext = norm.interval(0.99, avg_error_ext, std_error_ext)
            # span_95_ext = norm.interval(0.95, avg_error_ext, std_error_ext)

            # heurestic confidence interval
            # std_dev_heu = math.sqrt(var_error_heu)
            # std_error_heu = std_dev_heu / math.sqrt(sample_size)
            # span_99_heu = norm.interval(0.99, avg_error_heu, std_error_heu)
            # span_95_heu = norm.interval(0.95, avg_error_heu, std_error_heu)

            var_errors.append(var_error)
            # var_errors_ext.append(var_error_ext)
            # var_errors_heu.append(var_error_heu)
            
            res_string = "\nResult ALL DATA({}):\nSample size:{} triangles:{} test_data:{}\n".format(index, sample_size, len(estimates), sample_size)
            # log max ent result
            res_string += "avg_error:{} var_error:{}\n".format(avg_error, var_error)
            res_string += '99% Confidence interval(-/+): {}\n'.format(str(span_99))
            res_string += '95% Confidence interval(-/+): {}\n'.format(str(span_95))

            res_string += 'avg_error_ext:{} var_error_ext:{}\n'.format(avg_error_ext, var_error_ext)
            res_string += '99% Confidence interval(-/+): {}\n'.format(str(span_99_ext))
            res_string += '95% Confidence interval(-/+): {}\n'.format(str(span_95_ext))

            # res_string += 'avg_error_heu:{} var_error_heu:{}\n'.format(avg_error_heu, var_error_heu)
            # res_string += '99% Confidence interval(-/+): {}\n'.format(str(span_99_heu))
            # res_string += '95% Confidence interval(-/+): {}\n'.format(str(span_95_heu))

            with open(path + 'log.txt', 'a') as log_file:
                log_file.write(res_string)
            print res_string

            # Write result data
            with open(path + str(index) + '_data.json', 'w') as fd:
                # triplet_key = ['triple' for t in estimates]
                # est_key = ['est' for t in estimates]
                # obs_key = ['obs' for t in observations]
                fd.write(json.dumps(zip(triplets, zip(estimates, observations))))
            with open(path + str(index) + '_data.tsv', 'w') as fd:
                fd.write('est\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')
                for _index, i in enumerate(estimates):
                    fd.write(str(estimates[_index]) + '\t' + str(observations[_index]) + '\t' + str(triplets[_index][0]) + '\t' + str(triplets[_index][1]) + '\t' + str(triplets[_index][2]) + '\t' + str(pair_triple_ratios[_index]) + '\t' + str(triangle_counts[_index][0]) + '\t' + str(triangle_counts[_index][1]) + '\t' + str(triangle_counts[_index][2]) + '\t' + str(triangle_counts[_index][3]) + '\t' + str(triangle_counts[_index][4]) + '\t' + str(triangle_counts[_index][5]) + '\t' + str(triangle_counts[_index][6]) + '\n')
            with open(path + str(index) + '_data_extrapolation.tsv', 'w') as fd:
                fd.write('est\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')
                for _index, i in enumerate(estimates):
                    fd.write(str(extrapolations[_index]) + '\t' + str(observations[_index]) + '\t' + str(triplets[_index][0]) + '\t' + str(triplets[_index][1]) + '\t' + str(triplets[_index][2]) + '\t' + str(pair_triple_ratios[_index]) + '\t' + str(triangle_counts[_index][0]) + '\t' + str(triangle_counts[_index][1]) + '\t' + str(triangle_counts[_index][2]) + '\t' + str(triangle_counts[_index][3]) + '\t' + str(triangle_counts[_index][4]) + '\t' + str(triangle_counts[_index][5]) + '\t' + str(triangle_counts[_index][6]) + '\n')
            del estimates
            del observations

            # remove tmp files
            # os.remove(sample_freq_name)
            # os.remove(sample_file_name)

        else:
            print 'No abs errors!'

    print "Cross validation done!"
    print "time: ", (time() - cv_start)
    if len(avg_errors) > 0:
        total_avg_error = sum(avg_errors)/float(len(avg_errors))
        total_res_string = "Avg error:{}".format(total_avg_error)



      

def cross_validation(transactions, all_frequent_items=None, support=-3 ):
    """
    Does 1 to 10 sized cross validation
    May take 359.3s for 624252 transactions with 10% sample size
    """
    # init
    _id = str(time()).replace('.','')
    # if all_frequent_items is None:
    #     all_frequent_items = fpgrowth(transactions, supp=support, min=1, max=3)

    print "\n### Running cross validation {}###".format(_id)
    print "Total transactions:{}".format(len(transactions))
    # print "Total frequest items:{}".format(len(all_frequent_items))

    # run results
    avg_errors = []
    var_errors = []

    # all_triangles, all_triples = filter_items(all_frequent_items)

    for chunk, index, rest in chunks(transactions, len(transactions)/4):# TODO insert proper sampling
        
        start_first_chunk = time.time()
        
        print 'running fp-growth on rest'
        
        all_frequent_items = fpgrowth(rest, supp=support, min=1, max=3) # fp-growth on rest
        all_triangles, all_triples = filter_items(all_frequent_items)

        if len(all_frequent_items) > 0:
            print 'number of all frequent items: {}'.format(len(all_frequent_items))
            print 'number of all triangles: {}'.format(len(all_triangles))
            print 'number of all triples: {}'.format((len(all_triples)))
        else:
            print 'No frequent items in rest: {}'.format(index)
            continue
        after_first_part = time.time()-start

        print 'Have runed fp-growth on rest in ', after_first_part, ' secconds.'

        # Get triples for estimates
        print 'running fp fp-growth on chunk'
        frequent_items = fpgrowth(chunk, supp=-3, min=1, max=3) #fp-growth on chunk
        if len(frequent_items) > 0:
            print 'frequent items: {}'.format(len(frequent_items))
        else:
            print 'No frequent items in chunk: {}'.format(index)
            continue
        triangles, triples = filter_items(frequent_items)
        print 'triangles: {}'.format(len(triangles))
        print 'triples: {}'.format(len(triples))
        after_second_part = time.time()-after_first_part
        print 'Have runed fp-growth on chunk in ', after_second_part, ' secconds.'

        print 'now estimating tripple counts in rest'
        

        estimates = []
        observations = []
        abs_errors = []
        max_est = 0
        max_obs = 0

        for (s1, s2, s3, s12, s23, s13, s123) in triangles:

            # if s123[1] != 0:
            #     continue
            # maxent estimate from the sample. 
            # Index [1] of the tuples hold the # occurences in the sample
            est = maxent_est_rosa(s1[1], s2[1], s3[1], s12[1], s23[1], s13[1], float(len(transactions)-len(chunk)), num=int(math.log(len(transactions), 2))+1)

            # maxumum estiamte seen (for plotting)
            max_est = max(max_est, est)

            # record the estimate
            estimates.append(est)

            # from all observed triples get the actual observed number of triples
            observed = 0
            if all_triples.has_key(s123[0]):
                observed = all_triples[s123[0]]

            # maximum observation of the triple (for plotting)
            max_obs = max(max_obs, observed)

            # record the observed
            observations.append(observed)

            # record abs error
            abs_errors.append(abs(est-observed))

            
        if len(abs_errors) > 0: #TODO handle this, probably when nothing has been found
            # evaluation
            min_error = min(abs_errors)
            max_error = max(abs_errors)
            avg_error = sum(abs_errors) / float(len(abs_errors))
            avg_errors.append(avg_error)
            var_error = 0
            if len(abs_errors) > 1:
                var_error = tvar(abs_errors) #tvar is the sample variance
            var_errors.append(var_error)
            
            res_string = "\nResult:\nSample size:{} min_error:{} max_error:{} avg_error:{} var_error:{}".format(len(chunk), min_error, max_error, avg_errors[-1], var_error)
            print res_string

            # plot observed vs estmate
            fig = plt.figure()
            fig.text(0, 0, res_string)
            sub = fig.add_subplot(111)
            sub.scatter(estimates, observations)
            # plot optimal line
            scale = 1.5
            sub.plot([0, max_obs*scale], [0,max_obs*scale], color='r')

            sub.set_xlim([-1,max_est*scale])
            sub.set_ylim([-1,max_obs*scale])

            plt.xlabel('est')
            plt.ylabel('obs')
            folder = '../tmp/plots/cross_val/' + _id + '/'
            if not os.path.exists(folder):
                os.mkdir(folder)
            fig.savefig(folder  + str(index) + '.png')
            # plt.show()
            
        else:
            print 'No abs errors!'
        after_estimating = time.time() - after_second_part
        print 'Have estimated tripples in: ', after_estimating, ' secconds.'

    print "Cross validation done!"
    total_avg_error = sum(avg_errors)/float(len(avg_errors))
    total_res_string = "Avg error:{}".format(total_avg_error)


def est_all_data(frequent_items, total_transactions):
    print 'est all data2'
    start = time()
    transactions = None
    #transactions = parser.parse_csv_to_mat('/Users/ahkj/Dropbox/SAAS/data/csv/sample-big/customers.txt')
    all_frequent_items = fpgrowth(transactions, supp=-10, min=1, max=3) #-10 yields 3437
    M, triples = filter_items(all_frequent_items)
    fp_time = time() - start
    print "Finding frequent items: {}".format(fp_time)

    est_start = time()

    est = []
    obs = []
    abs_errors = []
    max_est = 0
    max_obs = 0
    i = 0
    j = 0

    triangle_start = time()
    triangle_tree, triples = Forward.forward_compact(frequent_items)
    print 'Finding triangles done: ', (time()-triangle_start)

    # DFS the triangle tree
    for n1 in triangle_tree.keys():
        s1, s2_dict = triangle_tree[n1]
        for n2 in s2_dict.keys():
            s2, s12, s3_dict = s2_dict[n2]
            for n3 in s3_dict.keys():
                s3, s13, s23, s123 = s3_dict[n3]
                if s123 < 30:
                    continue

                e = ent.maxent_est_rosa(s1, s2, s3, s12, s23, s13, float(total_transactions), num=20)

                est.append(e)
                obs.append(s123)
                error = abs(e-s123) / float(s123) * 100
                    
                abs_errors.append(error)

                # For plotting
                max_est = max(max_est, e)
                max_obs = max(max_obs, s123)

    with open('../tmp/est_all_data.json', 'w') as fd:
        fd.write(json.dumps(zip(est, obs)))
    with open('../tmp/est_al_data.tsv', 'w') as fd:
        fd.write('est\tobs\tkind\n')
        for index, i in enumerate(est):
            fd.write(str(est[index]) + '\t' + str(obs[index]) + '\t' + 'est/obs\n')
    # scale = 1.5

    # fig = plt.figure()
    # fig.text(0, 0, "Total running time: {} sec.".format(time()-est_start))
    avg_error = sum(abs_errors) / float(len(abs_errors))
    print 'avg error: {}'.format(avg_error)
    print 'error var: {}'.format(np.var(abs_errors))
    print 'max observed: {}'.format(max_obs)
    # sub = fig.add_subplot(111)
    # sub.scatter(est, obs)
    # sub.plot([0,max_obs*scale],[0,max_obs*scale], color='r')

    # sub.set_xlim([-1, max_est*scale])
    # sub.set_ylim([-1, max_obs*scale])

    # plt.xlabel('est')
    # plt.ylabel('obs')
    # fig.savefig('../tmp/plots/full_set.png')
    # plt.show()

est_all_data_disc_version(env.BORGELT_ALGORITHM, env.AOL_1M)
