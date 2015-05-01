"""
Plot errors against triple frequency over lowest pair frequency.
"""
def plot_ratios(output_folder):
    from parsers import CVOutputParser
    from utils import interpolate
    import math
    from collections import Counter
    import os
    """
    Plot accumulated errors for estimators agains pari triple ratios.
    Ratios are binned in the range 0.0 to 1.0.
    """
    if not output_folder[-1] == '/':
        output_folder += '/'

    pair_triple_ratios = [i/10. for i in range(11)]
    max_ent_ratio_error = [0 for i in range(11)]
    ext_ratio_error = [0 for i in range(11)]
    maxent_better_ratio = [0 for i in range(11)]
    ext_better_ratio = [0 for i in range(11)]
    values_binned = 0
    values_ignored = 0
    iteration = 0
    pair_counts = Counter()
    trip_counts = Counter()
    while True:
        max_ent_est_file = output_folder + str(iteration) + '_data.tsv'
        ext_est_file = output_folder + str(iteration) + '_data_extrapolation.tsv'
        # heu_est_file = output_folder + str(iteration) + '_data_heurestic.tsv'
        # read baseline also?
        # Read until we do not find an output file
        if not os.path.exists(max_ent_est_file):
            break

        max_ent_est = CVOutputParser.read_est_obs_file(max_ent_est_file)
        ext_est = CVOutputParser.read_est_obs_file(ext_est_file)
        # heu_est = CVOutputParser.read_est_obs_file(heu_est_file)

        for triple in max_ent_est.keys():

            (s1, s2, s3, s12, s13, s23, s123) = max_ent_est[triple][3]
            pair_counts[s12] += 1
            pair_counts[s13] += 1
            pair_counts[s23] += 1
            trip_counts[s123] += 1



            # if not s123 < max_trips or not min(s12, s13, s23) > min_pairs:
            #     values_ignored += 1
            #     continue
            # Index 1 should hold the observed value parsed from the file
            # is the same mapped to every estimate, so just read it once.
            obs = max_ent_est[triple][1]

            # if obs < 200:
            #     values_ignored += 1
            #     continue

            if obs < 200:
                continue

            # maxent estimate
            est = max_ent_est[triple][0]

            # extrapolation estimate
            est2 = ext_est[triple][0]

            # # independence estimat?

            # heurestic, use max_ent for 0 triple in sample
            # est4 = heu_est[triple][0]

            # Index 2 should hold the pair triple ratio.
            # is the sam for every estimat
            ratio = max_ent_est[triple][2]
            # bin the ratio to one decimal
            ratio_binned = round(ratio, 1)

            # Record the ratio if maxent was better
            maxent_error = abs(est-obs)/math.sqrt(obs)
            ext_error = abs(est2-obs)/math.sqrt(obs)

            try:
                if maxent_error < ext_error:
                    maxent_better_ratio[pair_triple_ratios.index(ratio_binned)] +=1
                elif maxent_error > ext_error:
                    ext_better_ratio[pair_triple_ratios.index(ratio_binned)] +=1
            except ValueError, ve:
                pass

            # add errors to the ratio bin
            try:
                values_binned += 1
                max_ent_ratio_error[pair_triple_ratios.index(ratio_binned)] += maxent_error
                ext_ratio_error[pair_triple_ratios.index(ratio_binned)] += ext_error
            except ValueError, ve:
                pass

        iteration += 1
        print 'iteration: ', iteration
    print 'values binned: ', values_binned
    print 'values ignored: ', values_ignored
    print max_ent_ratio_error
    print ext_ratio_error

    # interpolate(max_ent_ratio_error)
    # interpolate(ext_ratio_error)

    # plot(pair_triple_ratios, max_ent_ratio_error, color='blue')
    # plot(pair_triple_ratios, ext_ratio_error, color='red')
    xticks(pair_triple_ratios)
    xlabel('Triple/pair ratio')
    ylabel('Accumulated, normalized error')
    hist([pair_triple_ratios,pair_triple_ratios], weights=[max_ent_ratio_error, ext_ratio_error], bins=pair_triple_ratios, color=('b','r'))
    # savefig('pair_triple_ratio_error.png')
    # hist([pair_triple_ratios,pair_triple_ratios], weights=[maxent_better_ratio, ext_better_ratio,], bins=pair_triple_ratios, color=('b','r'))
    return pair_counts, trip_counts, maxent_better_ratio, ext_better_ratio, max_ent_ratio_error, ext_ratio_error, pair_triple_ratios

def error_ratios(output_folder, s_min=None, p_min=None, t_max=None, obs_min=None):
    """
    Error ratio against triple count in sample on a CV result.
    Needs the merged_estimates.tsv file that can be created
    with the relevant script in utils.py
    """

    from parsers import CVOutputParser
    from utils import interpolate, avg
    import math
    from collections import Counter
    import os

    if not output_folder[-1] == '/':
        output_folder += '/'

    max_singleton_occurrence = -1
    max_pair_occurrence = -1
    max_triple_occurrence = -1
    #max ent
    occurrence_ratio_errors = [0 for x in range(100000)]
    ratio_errors = []
    occurrences = [0 for x in range(100000)]
    merged_file = output_folder + 'merged_estimates.tsv'
    maxent_errors = []
    ext_errors = []
    iteration = 0
    maxent_was_best_estimates = []
    ext_was_best = []
    for (n1, n2, n3), (est, ext, obs, ratio, triangle) in CVOutputParser.read_merged_file_disc_version(merged_file):

        s1, s2, s3, s12, s13, s23, s123 = triangle

        iteration += 1
        if iteration % 1000000 == 0:
            print 'iteration: ', iteration

        if not s_min is None:
            if not min(s1,s2,s3) > s_min:
                continue
        if not p_min is None:
            if not min(s12,s23,s13) > p_min:
                continue
        if not t_max is None:
            if not s123 < t_max:
                continue

        if not obs_min is None:
            if not obs > obs_min:
                continue



        if max(s1,s2,s3) > max_singleton_occurrence:
            max_singleton_occurrence = max(s1,s2,s3)
        if max(s12,s13,s23) > max_pair_occurrence:
            max_pair_occurrence = max(s12,s13,s23)
        if s123 > max_triple_occurrence:
            max_triple_occurrence = s123

        # get the absolute errors, 
        # if this is below one we 
        # set it to one to avoid problems
        # with dividing with numbers < 1
        abs_ext_obs = abs(ext-obs)
        if abs_ext_obs < 1:
            abs_ext_obs = 1
        abs_est_obs = abs(est-obs)
        if abs_est_obs < 1:
            abs_est_obs = 1

        error = math.log(abs_est_obs / abs_ext_obs)
        ratio_errors.append(error)

        # low max ent estimate, magic numer is the value for the estiamtes
        # when a pair value was 1 for maxent, or 1 for ext
        # if est <= 104.0324:
        if error < 0:
            maxent_was_best_estimates.append(((n1, n2, n3), (est, ext, obs, ratio, triangle)))
        elif error > 0:
            ext_was_best.append(((n1, n2, n3), (est, ext, obs, ratio, triangle)))


        maxent_errors.append(est / float(obs))
        ext_errors.append(ext / float(obs))
        try:
            occurrences[int(obs)] += 1
            occurrence_ratio_errors[int(obs)] += error
        except IndexError, e:
            pass

    for i, count in enumerate(occurrences):
        if count > 0:
            occurrence_ratio_errors[i] = occurrence_ratio_errors[i] / float(count)

    print 'ratio error: ', sum(ratio_errors) / float(len(ratio_errors))
    print 'max_singleton_occurrence: ', max_singleton_occurrence
    print 'max_pair_occurrence: ', max_pair_occurrence
    print 'max_triple_occurrence: ', max_triple_occurrence

    # max_val = 1000
    # offset = 30
    # hist([x for x in range(max_val)[offset:]], ratio_errors[offset:max_val], color='green')

    return occurrence_ratio_errors, occurrences, maxent_errors, ext_errors, ratio_errors
    # return maxent_was_best_estimates, ext_was_best

def hist_observed_values(estiamtes):
    from scipy.stats import pearsonr
    # from utils import mid_inter_quantile
    total = len(estiamtes)
    observed = []
    for (n1, n2, n3), (est, ext, obs, ratio, triangle) in estiamtes:
        s1, s2, s3, s12, s13, s23, s123 = triangle

        observed.append(obs)

    print 'Total observed {}'.format(total)

    # bins=list(xrange(0, 500, 50))
    # xticks(bins)
    xlabel('Triples observed')
    ylabel('Bucket size')
    # observed.sort()
    # observed.reverse()
    hist(observed, color=('yellow',), bins=list(xrange(30, 200, 20)))
    # plot(range(500)[30:], observed[:470], color='yellow')

def analyse_maxent_low_estimates(maxent_low_estimates):
    from scipy.stats import pearsonr
    # from utils import mid_inter_quantile
    total = len(maxent_low_estimates)
    observed = []
    maxent_estimates = []
    ext_estimates = []
    max_ent_estiamte = 0
    ext_estiamte = 0
    min_pair_counts = 0
    zero_triples = 0
    for (n1, n2, n3), (est, ext, obs, ratio, triangle) in maxent_low_estimates:
        s1, s2, s3, s12, s13, s23, s123 = triangle
        if est <= 104.0324:
            continue
            
        if min(s1, s23, s13) == 1:
            min_pair_counts += 1
        if s123 == 0:
            zero_triples += 1

        max_ent_estiamte += est
        ext_estiamte += ext

        observed.append(obs)
        maxent_estimates.append(est)
        ext_estimates.append(ext)

    print 'Total sample points {}'.format(len(observed))
    print 'Min pairs equal 1 count: {}'.format(min_pair_counts)
    print 'Triples was 0 count {}'.format(zero_triples)
    print 'Observed average {}'. format(sum(observed) / float(len(observed)))
    print 'maxent_estimates average {}'. format(sum(maxent_estimates) / float(len(maxent_estimates)))
    print 'extrapolation average {}'. format(sum(ext_estimates) / float(len(ext_estimates)))
    print 'Observed, estimates correlation {}'.format(pearsonr(maxent_estimates, observed))
    observed.sort()
    maxent_estimates.sort()
    ext_estimates.sort()
    bins=list(xrange(0, 220, 20))
    xticks(bins)
    xlabel('Triples observed or estimated')
    ylabel('Bucket size')
    hist([observed, maxent_estimates, ext_estimates], color=('yellow', 'blue', 'red'), bins=bins)


# error_ratios('../tmp/200000_30supp_50samples/')

def error_ratios_cross_val(output_folder):
    """
    Cross validation on the error ratios to find optimal
    triangle values
    """

    from parsers import CVOutputParser
    from utils import avg

    if not output_folder[-1] == '/':
        output_folder += '/'


    singleton_thresholds = [0, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000]
    pair_thresholds = [0, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]
    triple_thresholds = [0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250]
    # Results are inserted at an offset
    # acc_error, count, maxent_best, ext_best
    c = [[[(0,0,0,0, (0,0,0)) for z in range(len(triple_thresholds))] for y in range(len(pair_thresholds))] for x in range(len(singleton_thresholds))]


    merged_file = output_folder + 'merged_estimates.tsv'

    iteration = 0
    for (n1, n2, n3), (est, ext, obs, ratio, triangle) in CVOutputParser.read_merged_file_disc_version(merged_file):

        s1, s2, s3, s12, s13, s23, s123 = triangle

        # Calculate errors and add the to the result matrix
        # Ratio error between estiamtes
        error = 0
        # check if both estimaters are spot on:
        if abs(ext-obs) == 0 and abs(est-obs) == 0:
            error = 1.
        # check that we are not dividing be a very small floating point
        # from extrapolation. If below one we just treat the error as
        # if it was 1
        if abs(ext-obs) < 1:
            error = float(abs(est-obs))
        # Get error ratio, avoid division by zero
        elif abs(ext-obs) != 0:
            error = abs(est-obs) / float(abs(ext-obs))
        # ratio_errors.append(error)
        for singleton_index, singleton_threshold in enumerate(singleton_thresholds):
            if not min(s1, s2, s3) > singleton_threshold:
                break
            for pair_index, pair_threshold in enumerate(pair_thresholds):
                if not min(s12, s13, s23) > pair_threshold:
                    break
                for triple_index, triple_threshold in enumerate(triple_thresholds):
                    if not s123 < triple_threshold:
                        continue
                    acc_error, count, maxent_best, ext_best, (s, p, t) = c[singleton_index][pair_index][triple_index]
                    acc_error += error
                    count += 1
                    if error < 1:
                        maxent_best += 1
                    elif error > 1:
                        ext_best += 1
                    c[singleton_index][pair_index][triple_index] = (acc_error, count, maxent_best, ext_best, (singleton_threshold, pair_threshold, triple_threshold))
        if iteration % 1000000 == 0:
            print 'iteration: ', iteration
        iteration += 1

        # maxent_errors.append(est / float(obs))
        # ext_errors.append(ext / float(obs))

    # Compute average errors
    for singleton_index, singleton_threshold in enumerate(singleton_thresholds):
        for pair_index, pair_threshold in enumerate(pair_thresholds):
            for triple_index, triple_threshold in enumerate(triple_thresholds):
                (acc_error, count, maxent_best, ext_best, (s,p,t)) = c[singleton_index][pair_index][triple_index]
                if count > 0:
                    c[singleton_index][pair_index][triple_index] = (acc_error / float(count), count, maxent_best, ext_best, (s,p,t))

    # ratio_error = sum(ratio_errors) / float(len(ratio_errors))
    # ext_ratio = avg(ext_errors)
    # maxent_ratio = avg(maxent_errors)

    # print 'Singletons done for threshold: ', singleton_threshold

    # fd.close()

    # fd = open(output_folder + 'parameter_cv.tsv', 'wr')
    # fd.write('singleton\tpair\ttriple\tmax_ent\text\tratio_error\n')
    # fd.write(singleton + '\t' + pair + '\t' + triple + '\t' + maxent_ratio + '\t' + ext_ratio + '\t' + ratio_error + '\n')
    # max_val = 1000
    # offset = 30
    # hist([x for x in range(max_val)[offset:]], ratio_errors[offset:max_val], color='green')

    return c

def plot_sorted_ratios(ratios, skip, color):
    """
    Plot aggregated ratio plot.
    skip specifies how many values are skipepd from ratios
    """
    sorted_ratios = sort(ratios[::skip])
    xs = list(xrange(0, len(ratios), skip))
    sorted_ratios = [x for x in sorted_ratios if x < 10]
    xs = xs[:len(sorted_ratios)]
    print len(sorted_ratios)
    print len(xs)
    ylabel('Error ratio')
    xlabel('Triples')
    plot(xs, sorted_ratios, color=color)
    plot(xs, [0 for x in xs])
    return sort(ratios)

def min_errors(cube):
    """
    Scratch pad code for searching the
    cube from singleton, pai, triple,
    cross validation
    """
    # acc_error, count, maxent_best, ext_best, ratio(maxent_best/ext_best)
    min_error = (100, 0, 0, 0, 0.0, ('','',''))
    for singleton_index, singleton_threshold in enumerate(singleton_thresholds):
        for pair_index, pair_threshold in enumerate(pair_thresholds):
            for triple_index, triple_threshold in enumerate(triple_thresholds):
                error, count, maxent_best, ext_best, (s,p,t) = c[singleton_index][pair_index][triple_index]
                ratio = maxent_best
                if ext_best > 0:
                    ratio = maxent_best / float(ext_best)
                if ratio > min_error[4]:
                    min_error = (error, count, maxent_best, ext_best, ratio, (s, p, t))
    return min_error

def to_list(cube):
    """
    Parse cube to a List containing values error, count, maxent_best, ext_best, ratio (s,p,t)
    """
    l = []
    # acc_error, count, maxent_best, ext_best, ratio(maxent_best/ext_best)
    for singleton_index, singleton_threshold in enumerate(singleton_thresholds):
        for pair_index, pair_threshold in enumerate(pair_thresholds):
            for triple_index, triple_threshold in enumerate(triple_thresholds):
                error, count, maxent_best, ext_best, (s,p,t) = cube[singleton_index][pair_index][triple_index]
                ratio = maxent_best
                if ext_best > 0:
                    ratio = maxent_best / float(ext_best)
                l.append((error, count, maxent_best, ext_best, ratio, (s,p,t)))
    l = [x for x in l if x[0] != 0 and x[5][0] != 0 and x[5][1] != 0 and x[5][2] != 0 ]
    # sort by error
    l.sort(lambda x,y : x[0] < y [0] and -1 or 1)
    return l

    # maxent_sorted = plot_sorted_ratios(maxent_errors, 1, 'b')
    # ext_sorted = plot_sorted_ratios(ext_errors, 1, 'r')

def transform_cube_to_bins(cube):
    new_cube=[[[]]]
    for singleton_index, singleton_threshold in enumerate(singleton_thresholds):
        if singleton_index+1 < len(singleton_thresholds):
            for pair_index, pair_threshold in enumerate(pair_thresholds):
                if pair_index+1 < len(pair_thresholds):
                    for triple_index, triple_threshold in enumerate(triple_thresholds):
                        if triple_index+1 < len(triple_thresholds):
                            new_cube[singleton_index][pair_index][triple_index] = cube[singleton_index-cube[singleton_index+1][pair_index][triple_index]][pair_index-cube[singleton_index][pair_index+1][triple_index]][triple_index-cube[singleton_index][pair_index][triple_index+1]]
    return new_cube
