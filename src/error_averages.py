# Helper scripts for computing error averages 
# related to triple counts
# Expects use of occurrencess, and accumulated average
# erros for relevant estimator
from utils import interpolate
# read in files
max_ent_acc_errors = pickle.load(open('max_ent_acc_error.pickle', 'r'))
ext_acc_errors = pickle.load(open('ext_acc_error.pickle', 'r'))
ind_acc_errors = pickle.load(open('ind_acc_error.pickle', 'r'))
baseline_acc_errors = pickle.load(open('baseline_acc_error.pickle', 'r'))
heu_acc_errors = pickle.load(open('heu_acc_error.pickle', 'r'))
occurrences = pickle.load(open('triple_occurrences.pickle', 'r'))


# Compute average values, from the 
# accumulated averages
for i, count in enumerate(occurrences):
    if count > 0:
        ext_acc_errors[i] = ext_acc_errors[i] / count
        max_ent_acc_errors[i] = max_ent_acc_errors[i] / count
        ind_acc_errors[i] = ind_acc_errors[i] / count
        heu_acc_errors[i] = heu_acc_errors[i] / count
        baseline_acc_errors[i] = baseline_acc_errors[i] / count


interpolate(ext_acc_errors)
interpolate(max_ent_acc_errors)
interpolate(ind_acc_errors)
interpolate(heu_acc_errors)
interpolate(baseline_acc_errors)

max_count = 100
plot(range(max_count), max_ent_acc_errors[:max_count], color='blue')
plot(range(max_count), ext_acc_errors[:max_count], color='red')
# plot(range(max_count), ind_acc_errors[:max_count], color='green')
# plot(range(max_count), heu_acc_errors[:max_count], color='yellow')
# plot(range(max_count), baseline_acc_errors[:max_count], color='purple')


def calc_avg_errors(output_folder):

    from parsers import CVOutputParser
    from utils import interpolate, avg
    import math
    from collections import Counter
    import os
    """ 
    Average error calculation on CV output.
    """
    if not output_folder[-1] == '/':
        output_folder += '/'
    
    # better_than_baseline_file = open('better_than_base_line.tsv', 'w')
    # better_than_baseline_file.write('est\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')

    # small_error_file = open('small_error.tsv', 'w')
    # small_error_file.write('est\tobs\tn1\tn2\tn3\tpair_trip_ratio\ts1\ts2\ts3\ts12\ts13\ts23\ts123\n')    
    baseline = 88.5
    iteration = 0
    points_evaluated = 0
    over_estimates = 0
    all_sample_errors = []
    while True:
        tsv_file = output_folder + str(iteration) + '_data_zero_trips.tsv'

        if not os.path.exists(tsv_file):
            break

        sample_erros = []
        for (n1, n2, n3), (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version_2(tsv_file):

            s1, s2, s3, s12, s13, s23, s123 = triangle

            # if int(obs) < 200 or s123 == 0:
            #     continue

            # Heurestiv for extrapolation, 200000 in sample
            # est = min(s12, s13, s23) / 200000. * (21006480-200000)

            points_evaluated += 1
            if est > obs:
                over_estimates += 1

            # if obs > baseline:
            #     if abs(est-obs) < abs(est-baseline):
            #         better_than_baseline_file.write(str(est) + '\t' + str(obs) + '\t' + str(n1) + '\t' + str(n2) + '\t' + str(n3) + '\t' + str(ratio) + '\t' + str(s1) + '\t' + str(s2) + '\t' + str(s3) + '\t' + str(s12) + '\t' + str(s13) + '\t' + str(s23) + '\t' + str(s123) + '\n')

            error = abs(est-obs) / math.sqrt(obs)
            # if error < 3:
            #     small_error_file.write(str(est) + '\t' + str(obs) + '\t' + str(n1) + '\t' + str(n2) + '\t' + str(n3) + '\t' + str(ratio) + '\t' + str(s1) + '\t' + str(s2) + '\t' + str(s3) + '\t' + str(s12) + '\t' + str(s13) + '\t' + str(s23) + '\t' + str(s123) + '\n')
            sample_erros.append(error)
        all_sample_errors.append(avg(sample_erros))
        iteration += 1

    # better_than_baseline_file.close()
    # small_error_file.close()

    avg_error = avg(all_sample_errors)
    print 'avg_error ', avg_error
    print 'points evaluated', points_evaluated
    print 'over estimates: ', over_estimates
    return avg_error, all_sample_errors

def error_averages_for_triple_counts(output_folder):
    """
    Accumulated errors against triple count in sample on a CV result
    """
    from parsers import CVOutputParser
    from utils import interpolate, avg
    import math
    from collections import Counter
    import os
    """ 
    Average error calculation on CV output.
    """
    if not output_folder[-1] == '/':
        output_folder += '/'

    baseline = 88.5
    #max ent
    iteration = 0
    max_ent_acc_errors = [0 for x in range(100000)]
    baseline_acc_errors = [0 for x in range(100000)]
    occurrences = [0 for x in range(100000)]
    while True:
        tsv_file = output_folder + str(iteration) + '_data.tsv'

        if not os.path.exists(tsv_file):
            break

        for (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version(tsv_file):

            s1, s2, s3, s12, s13, s23, s123 = triangle

            # if obs < 200:
            #     continue

            try:
                occurrences[int(obs)] += 1
                max_ent_acc_errors[int(obs)] += abs(est-obs) / math.sqrt(obs)
                baseline_acc_errors[int(obs)] += abs(baseline-obs) / math.sqrt(obs)
            except IndexError, e:
                pass

        iteration += 1
        print 'iteration: ', iteration

    # extrapolation
    ext_acc_errors = [0 for x in range(100000)]
    iteration = 0
    while True:
        tsv_file = output_folder + str(iteration) + '_data_extrapolation.tsv'

        if not os.path.exists(tsv_file):
            break

        for (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version(tsv_file):

            s1, s2, s3, s12, s13, s23, s123 = triangle

            # if obs < 200:
            #     continue

            try:
                ext_acc_errors[int(obs)] += abs(est-obs) / math.sqrt(obs)
            except IndexError, e:
                pass

        iteration += 1
        print 'iteration: ', iteration

    for i, count in enumerate(occurrences):
        if count > 0:
            ext_acc_errors[i] = ext_acc_errors[i] / float(count)
            max_ent_acc_errors[i] = max_ent_acc_errors[i] / float(count)
            # ind_acc_errors[i] = ind_acc_errors[i] / count
            # heu_acc_errors[i] = heu_acc_errors[i] / count
            baseline_acc_errors[i] = baseline_acc_errors[i] / count

    max_val = 1000
    offset = 30
    ylabel('Avg. normalized error')
    xlabel('Triples observed x times in the test data')
    plot([x for x in range(max_val)[offset:]], max_ent_acc_errors[offset:max_val], color='b')
    plot([x for x in range(max_val)[offset:]], baseline_acc_errors[offset:max_val], color='purple')
    plot([x for x in range(max_val)[offset:]], ext_acc_errors[offset:max_val], color='r')
    # savefig('low_trips_observed_against_estimats.png')
    
    # savefig('low_trips_observed_against_estimats.png')
    return max_ent_acc_errors, ext_acc_errors, baseline_acc_errors, occurrences


def hist_of_triple_occurrences():
    xlabel('Triples observed x times in the test data')
    ylabel('Bucket size')
    xticks([30, 50, 100, 150, 200])
    hist(range(201), weights=occurrences[0:201], bins=range(201))
    savefig('triple_set_occurrences.png')