import env
import pickle
from scipy.stats import norm, tvar # sample variance
from entropy import Entropy as ent
from utils import chunks, triple_sort, avg
from time import time, sleep
from triangles import Forward
from preprocessing import Preprocessor
import math
import os
import sys
import json
import random
import subprocess
from collections import Counter


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


def cross_validate_disc_version(algorithm, tab_file, min_support=-30, sample_pct=0.1, iterations=1, only_interesting_triples=False, restricted_triples=None, extra_id=''):
    from subprocess import call
    from parsers import Borgelt

    cv_start = time()

    # Create work folder
    _id = str(time()).replace('.','') + '_' + extra_id
    path = '../tmp/cv_' + _id + '/'
    os.mkdir(path)
    print "\n### Running cross validation cv_{}###".format(_id)

    total_transactions = 0
    for line in open(tab_file, 'rb'):
        total_transactions += 1
    print 'Total total_transactions: ', total_transactions

    # Get the total observed triples
    borgelt_start = time()
    observed_file_name = path + 'observed_frequent_items.out'
    args = [algorithm, tab_file, observed_file_name, '-s' + str(min_support), '-n3']
    # pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    # os.killpg(pro.pid, signal.SIGTERM)
    call(args)
    # sleep(20)
    print 'fpgrowth on all data done: {} secs'.format(time()-borgelt_start)

    freq = Borgelt.read_frequent_items(observed_file_name)

    # Create ds of all observed triplets
    # Saved as sorted keys for lookup,
    # and their frequency as value
    observed = {}
    count = 0
    for item in freq:
        if len(item[0]) == 3:
            sorted_trip = triple_sort(item[0])
            observed[sorted_trip] = item[1][0]
    print 'Total triplets observed:', len(observed)
    average_observed = sum(observed.values()) / float(len(observed))
    print 'Baseline: ', average_observed

    del freq

    avg_errors = []
    var_errors = []
    avg_errors_ext = []
    var_errors_ext = []
    avg_errors_heu = []
    var_errors_heu = []
    avg_errors_ind = []
    var_errors_ind = []
    avg_errors_baseline = []

    occurrences = [0 for i in range(100)]
    max_ent_acc_error = [0 for i in range(100)]
    ext_acc_error = [0 for i in range(100)]
    ind_acc_error = [0 for i in range(100)]
    heu_acc_error = [0 for i in range(100)]
    baseline_acc_error = [0 for i in range(100)]

    # Record trip counts for the best estimats
    max_ent_best = Counter()
    ext_best = Counter()
    ind_best = Counter()

    for index in range(iterations):

        # Create sample file
        sampling_start = time()
        if sample_pct > 0:
            sample_size= int(total_transactions*sample_pct)
        else:
            sample_size = abs(sample_pct)
        test_data_size = total_transactions - sample_size
        sample = random.sample(range(total_transactions), sample_size)
        assert len(sample) == sample_size, 'Sample size not equal to sample'
        sample.sort()
        sample_file_name = path + str(index) + '_sample.tab'
        with open(sample_file_name, 'a') as sample_file:
            sample_line = 0
            for line_num, line in enumerate(open(tab_file, 'rb')):
                if line_num == sample[sample_line]:
                    sample_file.write(line)
                    sample_line += 1
                    if sample_line == sample_size:
                        break

        del sample
        print 'Sample size: {} time: {}'.format(sample_size, time() - sampling_start)
        borgelt_start = time()
        sample_freq_name = path + str(index) + '_sample_frequent_items.out'
        args = [algorithm, sample_file_name, sample_freq_name, '-s-1', '-n3']
        call(args)
        print 'fpgrowth on sample data done: {} secs'.format(time()-borgelt_start)

        # Check any frequent items were found
        if not os.path.exists(sample_freq_name):
            print 'No frequent items found'
            print 'args', args
            continue

        min_support_trips = min_supported_trips(min_support, test_data_size)
        print 'Forward min_support_trips set to: ', min_support_trips
        triangles_start = time()
        triangle_tree, sample_triples = Forward.forward_compact(sample_freq_name, min_support_trips, observed, only_interesting_triples, restricted_triples)
        print 'Found triangles done: {}'.format(time() - triangles_start)

        #del sample_freq

        estimates = []
        extrapolations = []
        independences = []
        heurestics = []
        baselines = []
        observations = []

        triplets = []
        MAPE_errors = []
        MAPE_errors_ext = []
        MAPE_errors_ind = []
        MAPE_errors_heu = []
        MAPE_errors_baseline = []
        true_errors = []
        pair_triple_ratios = []

        triangle_counts = []

        # s1_list = []
        # s2_list = []
        # s3_list = []
        # s12_list = []
        # s13_list = []
        # s23_list = []

        # Recursion for estimate to converge
        req_depth = int(math.log(total_transactions, 2)) + 1

        # DFS of the tree holding all triangles
        for n1 in triangle_tree.keys():
            s1, s2_dict = triangle_tree[n1]
            for n2 in s2_dict.keys():
                s2, s12, s3_dict = s2_dict[n2]
                for n3 in s3_dict.keys():
                    s3, s13, s23, s123 = s3_dict[n3]

                    triangle_counts.append((s1, s2, s3, s12, s13, s23, s123))

                    triangle = (n1, n2, n3)

                    pair_triple_ratio = s123 / float(min(s12, s13, s23))
                    pair_triple_ratios.append(pair_triple_ratio)

                    # Get the obs (test data) frequency minus those found in the sample (training data)
                    obs = 0
                    if triangle in observed:
                         # (triples in data) - (triples in sample). Calculating the number of triples in test data.
                        obs = observed[triangle] - s123

                    # maxent estimate
                    est = ent.maxent_est_rosa(s1, s2, s3, s12, s23, s13, float(sample_size), num=req_depth) * (test_data_size / float(sample_size))

                    if est < 0:
                        print 'max ent below 0'
                        print 's1 s2 s3 s12 s13 s23 s123', (s1, s2, s3, s12, s23, s13, s123)

                    # extrapolation estimate
                    est2 = s123 / float(sample_size) * test_data_size

                    # independence estimat
                    est3 = (s1 / float(sample_size)) * (s2 / float(sample_size)) * (s3 / float(sample_size)) * test_data_size
                    # est3 = (s1*s2*s3)/float(sample_size*sample_size) * test_data_size/float(sample_size)

                    # heurestic, use max_ent for 0 triple in sample
                    est4 = s123 < 5 and est or est2

                    # base line estimat
                    est5 = average_observed

                    estimates.append(est)
                    extrapolations.append(est2)
                    independences.append(est3)
                    heurestics.append(est4)
                    baselines.append(est5)
                    observations.append(obs)
                    triplets.append(triangle)
                    # TODO Do why save these? They already exist in the triangle tree (and take
                    # up shit load of space..)
                    # s1_list.append(s1)
                    # s2_list.append(s2)
                    # s3_list.append(s3)
                    # s12_list.append(s12)
                    # s13_list.append(s13)
                    # s23_list.append(s23)
                    #end TODO

                    # MAPE error max ent
                    error = abs(obs-est) / math.sqrt(obs) # * 100
                    MAPE_errors.append(error)
                    true_errors.append(obs-est)

                    # MAPE error extrapolation
                    error2 = 0
                    if est2 > 0:
                        error2 = abs(obs-est2) / math.sqrt(obs) # * 100
                    MAPE_errors_ext.append(error2)

                    # MAPE error independence
                    error3 = abs(obs-est3) / math.sqrt(obs) # * 100
                    MAPE_errors_ind.append(error3)

                    # MAPE error heurestic
                    error4 = abs(obs-est4) / math.sqrt(obs) # * 100
                    MAPE_errors_heu.append(error4)

                    # MAPE baseline error
                    error5 = abs(obs-est5) / math.sqrt(obs) #* 100
                    MAPE_errors_baseline.append(error5)

                    # Record error for the estimeate that performed best
                    if error < error2 and error < error3:
                        max_ent_best[s123] += 1
                    elif error2 < error and error2 < error3:
                        ext_best[s123] += 1
                    else:
                        ind_best[s123] += 1

                    try:
                        occurrences[s123] += 1
                        max_ent_acc_error[s123] += error
                        ext_acc_error[s123] += error2
                        ind_acc_error[s123] += error3
                        heu_acc_error[s123] += error4
                        baseline_acc_error[s123] += error5
                    except IndexError, ie:
                        pass


        # print 'true errors: ', true_errors
        # print 'estimates: ', estimates
        # print 'observed: ', observed
        # print 'mape ', MAPE_errors
        del triangle_tree
        del sample_triples

        if len(MAPE_errors) > 0: #TODO handle this, probably when nothing has been found

            min_error = min(MAPE_errors)
            max_error = max(MAPE_errors)

            # max ent error
            avg_error = sum(MAPE_errors) / float(len(MAPE_errors))
            avg_errors.append(avg_error)

            # extrapolation error
            avg_error_ext = sum(MAPE_errors_ext) / float(len(MAPE_errors_ext))
            avg_errors_ext.append(avg_error_ext)

            # independence error
            avg_error_ind = sum(MAPE_errors_ind) / float(len(MAPE_errors_ind))
            avg_errors_ind.append(avg_error_ind)

            # heurestic error
            avg_error_heu = sum(MAPE_errors_heu) / float(len(MAPE_errors_heu))
            avg_errors_heu.append(avg_error_heu)

            # baseline error
            avg_error_baseline = sum(MAPE_errors_baseline) / float(len(MAPE_errors_baseline))
            avg_errors_baseline.append(avg_error_baseline)

            var_error = 0
            var_error_ext = 0
            var_error_heu = 0
            var_error_ind = 0
            # variance
            if len(MAPE_errors) > 1:
                var_error = tvar(MAPE_errors) #tvar is the sample variance
                var_error_ext = tvar(MAPE_errors_ext)
                var_error_heu = tvar(MAPE_errors_heu)
                var_error_ind = tvar(MAPE_errors_ind)


            # max_ent confidence interval
            std_dev = math.sqrt(var_error)
            std_error = std_dev / math.sqrt(sample_size)
            span_99 = norm.interval(0.99, avg_error, std_error)
            span_95 = norm.interval(0.95, avg_error, std_error)

            # ext confidence interval
            std_dev_ext = math.sqrt(var_error_ext)
            std_error_ext = std_dev_ext / math.sqrt(sample_size)
            span_99_ext = norm.interval(0.99, avg_error_ext, std_error_ext)
            span_95_ext = norm.interval(0.95, avg_error_ext, std_error_ext)

            # independence confidence interval
            std_dev_ind = math.sqrt(var_error_ind)
            std_error_ind = std_dev_ind / math.sqrt(sample_size)
            span_99_ind = norm.interval(0.99, avg_error_ind, std_error_ind)
            span_95_ind = norm.interval(0.95, avg_error_ind, std_error_ind)

            # heurestic confidence interval
            std_dev_heu = math.sqrt(var_error_heu)
            std_error_heu = std_dev_heu / math.sqrt(sample_size)
            span_99_heu = norm.interval(0.99, avg_error_heu, std_error_heu)
            span_95_heu = norm.interval(0.95, avg_error_heu, std_error_heu)

            var_errors.append(var_error)
            var_errors_ext.append(var_error_ext)
            var_errors_heu.append(var_error_heu)
            var_errors_ind.append(var_error_ind)

            res_string = "\nResult ({}):\nSample size:{} triangles:{} test_data:{}\n".format(index, sample_size, len(estimates), total_transactions-sample_size)
            # log max ent result
            res_string += "avg_error:{} var_error:{}\n".format(avg_error, var_error)
            res_string += '99% Confidence interval(-/+): {}\n'.format(str(span_99))
            res_string += '95% Confidence interval(-/+): {}\n'.format(str(span_95))

            res_string += 'avg_error_ext:{} var_error_ext:{}\n'.format(avg_error_ext, var_error_ext)
            res_string += '99% Confidence interval(-/+): {}\n'.format(str(span_99_ext))
            res_string += '95% Confidence interval(-/+): {}\n'.format(str(span_95_ext))

            res_string += 'avg_error_ind:{} var_error_ind:{}\n'.format(avg_error_ind, var_error_ind)
            res_string += '99% Confidence interval(-/+): {}\n'.format(str(span_99_ind))
            res_string += '95% Confidence interval(-/+): {}\n'.format(str(span_95_ind))

            res_string += 'avg_error_heu:{} var_error_heu:{}\n'.format(avg_error_heu, var_error_heu)
            res_string += '99% Confidence interval(-/+): {}\n'.format(str(span_99_heu))
            res_string += '95% Confidence interval(-/+): {}\n'.format(str(span_95_heu))

            res_string += 'avg_error_baseline:{}\n'.format(avg_error_baseline)

            with open(path + str(index) + '_log.txt', 'a') as log_file:
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
            with open(path + str(index) + '_data_heurestic.tsv', 'w') as fd:
                fd.write('est\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')
                for _index, i in enumerate(heurestics):
                    fd.write(str(heurestics[_index]) + '\t' + str(observations[_index]) + '\t' + str(triplets[_index][0]) + '\t' + str(triplets[_index][1]) + '\t' + str(triplets[_index][2]) + '\t' + str(pair_triple_ratios[_index]) + '\t' + str(triangle_counts[_index][0]) + '\t' + str(triangle_counts[_index][1]) + '\t' + str(triangle_counts[_index][2]) + '\t' + str(triangle_counts[_index][3]) + '\t' + str(triangle_counts[_index][4]) + '\t' + str(triangle_counts[_index][5]) + '\t' + str(triangle_counts[_index][6]) + '\n')
            with open(path + str(index) + '_data_independece.tsv', 'w') as fd:
                fd.write('est\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')
                for _index, i in enumerate(independences):
                    fd.write(str(independences[_index]) + '\t' + str(observations[_index]) + '\t' + str(triplets[_index][0]) + '\t' + str(triplets[_index][1]) + '\t' + str(triplets[_index][2]) + '\t' + str(pair_triple_ratios[_index]) + '\t' + str(triangle_counts[_index][0]) + '\t' + str(triangle_counts[_index][1]) + '\t' + str(triangle_counts[_index][2]) + '\t' + str(triangle_counts[_index][3]) + '\t' + str(triangle_counts[_index][4]) + '\t' + str(triangle_counts[_index][5]) + '\t' + str(triangle_counts[_index][6]) + '\n')

            # Save the errors
            with open(path + str(index) + '_MAPE_errors.pickle', 'wb') as fd:
                pickle.dump(MAPE_errors, fd)
            with open(path + str(index) + '_MAPE_errors_ext.pickle', 'wb') as fd:
                pickle.dump(MAPE_errors_ext, fd)
            with open(path + str(index) + '_MAPE_errors_heu.pickle', 'wb') as fd:
                pickle.dump(MAPE_errors_heu, fd)
            with open(path + str(index) + '_MAPE_errors_ind.pickle', 'wb') as fd:
                pickle.dump(MAPE_errors_ind, fd)
            with open(path + str(index) + '_MAPE_errors_baseline.pickle', 'wb') as fd:
                pickle.dump(MAPE_errors_baseline, fd)

            #saves amounts of all subsets of triples.
            # TODO this code does not run!
            # with open(path + str(index) + '_data_correlations.tsv', 'w') as fd:
            #     fd.write('s1\ts2\ts3\ts12\ts13\ts23\n')
            #     for _index, i in enumerate(s123):
            #         fd.write(str(s1[_index]) + '\t' + str(s2[_index]) + '\t' + str(s3[_index]) + '\t' + str(s12[_index]) + '\t' + str(s13[_index]) + '\t'+ str(s23[_index]) + '\n')

            #saves independence estimate for all triples.
            # TODO Why s123[_index] in the denominator?
            # TODO What is a 'double independece estimat'?
            # TODO Why not calculate and save estimates in the same way as ext and max_ent?
            # with open(path + str(index) + '_independence_estimate.tsv', 'w') as fd:
            #     fd.write('single independence estimate\tdouble independence estimate\n')
            #     for _index, i in enumerate(s123):
            #     	tempVal1 = sample_size/(s1[_index])
            #     	tempVal2=sample_size/(s2[_index])
            #     	tempVal3=sample_size/(s3[_index])
            #     	tempVal12=sample_size/(s12[_index])
            #     	tempVal13=sample_size/(s13[_index])
            #     	tempVal23=sample_size/(s23[_index])
            #         fd.write(str(s123[_index]/tempVal1*tempVal2*tempVal3*(total_transactions-sample_size) + '\t' + s123[_index]/tempVal12*tempVal13*tempVal23*(total_transactions-sample_size) + '\n'))


            del estimates
            del observations

            # remove tmp files
            # os.remove(sample_freq_name)
            # os.remove(sample_file_name)

        else:
            print 'No abs errors!'

    # Save triple counts, accumulated errors, and average errors
    with open(path + 'avg_errors.pickle', 'wb') as fd:
        pickle.dump(avg_errors, fd)
    with open(path + 'avg_errors_ext.pickle', 'wb') as fd:
        pickle.dump(avg_errors_ext, fd)
    with open(path + 'avg_errors_ind.pickle', 'wb') as fd:
        pickle.dump(avg_errors_ind, fd)
    with open(path + 'avg_errors_heu.pickle', 'wb') as fd:
        pickle.dump(avg_errors_heu, fd)
    with open(path + 'avg_errors_baseline.pickle', 'wb') as fd:
        pickle.dump(avg_errors_baseline, fd)
    with open(path + 'triple_occurrences.pickle', 'wb') as fd:
        pickle.dump(occurrences, fd)
    with open(path + 'max_ent_acc_error.pickle', 'wb') as fd:
        pickle.dump(max_ent_acc_error, fd)
    with open(path + 'ext_acc_error.pickle', 'wb') as fd:
        pickle.dump(ext_acc_error, fd)
    with open(path + 'ind_acc_error.pickle', 'wb') as fd:
        pickle.dump(ind_acc_error, fd)
    with open(path + 'heu_acc_error.pickle', 'wb') as fd:
        pickle.dump(heu_acc_error, fd)
    with open(path + 'baseline_acc_error.pickle', 'wb') as fd:
        pickle.dump(baseline_acc_error, fd)
    print "Cross validation done!"
    # print 'avg errrors, ', avg_errors
    # print 'avg errrors ext, ', avg_errors_ext
    # print 'max_ent_best: ', max_ent_best
    # print 'ext_best: ', ext_best
    print 'occurrences: ', occurrences
    print 'max_ent_acc_error', max_ent_acc_error
    print 'ext_acc_error', ext_acc_error
    print "time: ", (time() - cv_start)
    if len(avg_errors) > 0:
        total_avg_error = sum(avg_errors)/float(len(avg_errors))
        total_res_string = "Avg error:{}".format(total_avg_error)
    return path


def cross_validation_compact(transactions, sample_pct=0.50, support=-3, all_frequent_items=None):
    from fim import fpgrowth
    """
    Cross validation. Using compact representation from
    Forward.
    """
    # init
    _id = str(time()).replace('.','')
    # if all_frequent_items is None:
    #     all_frequent_items = fpgrowth(transactions, supp=support, min=1, max=3)

    cv_start = time()
    print "\n### Running cross validation {}###".format(_id)
    print "Total transactions:{}".format(len(transactions))
    # print "Total frequest items:{}".format(len(all_frequent_items))

    # run results
    avg_errors = []
    var_errors = []

    # all_triangles, all_triples = filter_items(all_frequent_items)

    for chunk, index, rest in chunks(transactions, int(len(transactions) * sample_pct)):# TODO insert proper sampling

        all_frequent_items = fpgrowth(rest, supp=support, min=1, max=3)
        all_triangles, all_triples = Forward.forward_compact(all_frequent_items)

        # Get triples for estimates
        frequent_items = fpgrowth(chunk, supp=support, min=1, max=3)
        if len(frequent_items) > 0:
            print 'frequent items: {}'.format(len(frequent_items))
        else:
            print 'No frequent items in chunk: {}'.format(index)
            continue
        triangle_tree, triples = Forward.forward_compact(frequent_items)
        print 'triangle roots: {}'.format(len(triangle_tree))

        estimates = []
        observations = []
        abs_errors = []
        max_est = 0
        max_obs = 0

        # DFS of the tree holding all triangles
        for n1 in triangle_tree.keys():
            s1, s2_dict = triangle_tree[n1]
            for n2 in s2_dict.keys():
                s2, s12, s3_dict = s2_dict[n2]
                for n3 in s3_dict.keys():
                    s3, s13, s23, s123 = s3_dict[n3]

                    est = ent.maxent_est_rosa(s1, s2, s3, s12, s23, s13, float(len(transactions)-len(chunk)), num=int(math.log(len(transactions), 2))+1)

                    # maxumum estiamte seen (for plotting)
                    max_est = max(max_est, est)

                    # record the estimate
                    estimates.append(est)

                    # from all observed triples get the actual observed number of triples
                    observed = 0
                    if all_triples.has_key((n1, n2, n3)):
                        observed = all_triples[(n1, n2, n3)]

                    # maximum observation of the triple (for plotting)
                    max_obs = max(max_obs, observed)

                    # record the observed
                    observations.append(observed)

                    # record abs error
                    error = abs(obs-est) / float(obs) * 100
                    abs_errors.append(error)


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
        else:
            print 'No abs errors!'

    print "Cross validation done!"
    print "time: ", (time() - cv_start)
    total_avg_error = sum(avg_errors)/float(len(avg_errors))
    total_res_string = "Avg error:{}".format(total_avg_error)


def cross_validation(transactions, sample_pct=0.50, support=-3, all_frequent_items=None):
    from fim import fpgrowth
    """
    Cross validation, 'old' version not using compatct
    triangle representation from Forward.
    """
    # init
    _id = str(time()).replace('.','')
    # if all_frequent_items is None:
    #     all_frequent_items = fpgrowth(transactions, supp=support, min=1, max=3)

    cv_start = time()
    print "\n### Running cross validation {}###".format(_id)
    print "Total transactions:{}".format(len(transactions))
    # print "Total frequest items:{}".format(len(all_frequent_items))

    # run results
    avg_errors = []
    var_errors = []

    # all_triangles, all_triples = filter_items(all_frequent_items)

    for chunk, index, rest in chunks(transactions, int(len(transactions) * sample_pct)):# TODO insert proper sampling

        all_frequent_items = fpgrowth(rest, supp=support, min=1, max=3)
        all_triangles, all_triples = Forward.forward(all_frequent_items)

        # Get triples for estimates
        frequent_items = fpgrowth(chunk, supp=support, min=1, max=3)
        if len(frequent_items) > 0:
            print 'frequent items: {}'.format(len(frequent_items))
        else:
            print 'No frequent items in chunk: {}'.format(index)
            continue
        triangles, triples = Forward.forward(frequent_items)
        print 'triangles: {}'.format(len(triangles))

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
            est = ent.maxent_est_rosa(s1[1], s2[1], s3[1], s12[1], s23[1], s13[1], float(len(transactions)-len(chunk)), num=int(math.log(len(transactions), 2))+1)

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
            error = abs(obs-est) / float(obs) * 100
            abs_errors.append(error)



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

            # TODO histogram of the average errors. max-ent, extrapolation, heurestic
            # TODO print average error og the average errors to the log.

            res_string = "\nResult:\nSample size:{} min_error:{} max_error:{} avg_error:{} var_error:{}".format(len(chunk), min_error, max_error, avg_errors[-1], var_error)
            print res_string
        else:
            print 'No abs errors!'

    print "Cross validation done!"
    print "time: ", (time() - cv_start)
    total_avg_error = sum(avg_errors)/float(len(avg_errors))
    total_res_string = "Avg error:{}".format(total_avg_error)
    return path

def generate_intervals():
    # Script to generate a given number of frequency intervals given 
    # a frequent items output from Borgelt
    intervals = 30
    output_folders = []
    for interval, res in enumerate(Preprocessor.triple_intervals('../tmp/observed_frequent_items.out', intervals=intervals)):

        # Triple set of 1/intervals part of the data
        interval_id = 'interval_' + str(intervals) + '_' + str(interval)
        output_folder = cross_validate_disc_version(env.BORGELT_ALGORITHM, env.AOL_MERGED_FILE, sample_pct=-100000, iterations=2, restricted_triples=res, extra_id=interval_id, min_support=-30)
        output_folders.append(output_folder)
    print 'output folders: ', output_folders

def plot_intervals_restricted_cv(output_folders):
    # Intervals by indexes, the actual indexes can currently only be seen from the print out
    # from the preprocessor
    # Run this on a CV that has been run on restricted intervals
    intervals = range(len(output_folders))
    AVG_avg_errors = []
    AVG_avg_errors_baseline = []
    AVG_avg_errors_ext = []
    #AVG_avg_errors_heu = []
    #AVG_avg_errors_ind = []

    for index, folder in enumerate(output_folders):

        # save average of averages with the given interval
        avg_errors = pickle.load(open(folder + 'avg_errors.pickle', 'r'))
        avg_errors_baseline = pickle.load(open(folder + 'avg_errors_baseline.pickle', 'r'))
        avg_errors_ext = pickle.load(open(folder + 'avg_errors_ext.pickle', 'rb'))
        #avg_errors_heu = pickle.load(open(folder + 'avg_errors_heu.pickle', 'rb'))
        #avg_errors_ind = pickle.load(open(folder + 'avg_errors_ind.pickle', 'rb'))

        AVG_avg_errors.append(avg(avg_errors))
        AVG_avg_errors_baseline.append(avg(avg_errors_baseline))
        AVG_avg_errors_ext.append(avg(avg_errors_ext))
        #AVG_avg_errors_heu.append(avg(avg_errors_heu))
        #AVG_avg_errors_ind.append(avg(avg_errors_ind))

    # plot
    plot(intervals, AVG_avg_errors, color='blue')
    plot(intervals, AVG_avg_errors_ext, color='red')
    #plot(intervals, AVG_avg_errors_ind, color='green')
    #plot(intervals, AVG_avg_errors_heu, color='yellow')
    plot(intervals, AVG_avg_errors_baseline, color='purple')

        # iterate files, find these by the given id, get average of average max ent errors
        # run cv with x iterations, on this triple set with and create histogram of the average errors for each run
        # along the variance/std dev
        # compare difference in errors for max_ent vs extrapolation, depending on which fragment of the triples we have looked at.

        # For cv run log. Store one .tsv file with all averages, add run parameter id so we can post postfix with e.g. 1_30, 2_30

        # scatter plot the average of the average errors to compare max_ent to extrapolation. Wo see if they cross over at some point.



# plot_intervals('../tmp/cv_139885983932_')



# test_intervals()

cross_validate_disc_version(env.BORGELT_ALGORITHM, env.AOL_MERGED_FILE_TRIMMED, min_support=-30, sample_pct=-200000, iterations=50)

# cross_validate_disc_version(env.BORGELT_ALGORITHM, env.AOL_100k, min_support=-3, sample_pct=.5)
# print 'start'
# transactions = CSVParser.parse_csv_to_mat('/Users/ahkj/Dropbox/SAAS/data/csv/sample-big/customers.txt')
# cross_validation(transactions[:50000])
