import matplotlib.pyplot as plt
import numpy as np

"""

"""


def plot_destribution(triple, output_folder):
    from collections import Counter
    if not output_folder[-1] == '/':
       output_folder += '/'


    #triple_info = None
    maxent_estimates = Counter()
    ext_estimates = Counter()
    accumulated_ratio = 0
    number_of_measurements = 0
    # Ax 1 :pair_triple_ratios = [i/100. for i in range(11)]
    # Ax 2: max_ent_ratio_error = [0 for i in range(11)]
    #ext_ratio_error = [0 for i in range(11)]
    #values_binned = 0
    iteration = 0
    while True:
        max_ent_est_file = output_folder + str(iteration) + '_data.tsv'
        ext_est_file = output_folder + str(iteration) + '_data_extrapolation.tsv'
        #heu_est_file = output_folder + str(iteration) + '_data_heurestic.tsv'
        
        if not os.path.exists(max_ent_est_file):
            break
        # parsed results from CV to dictionary 
        max_ent_est = CVOutputParser.read_est_obs_file(max_ent_est_file)
        # also a dict
        ext_est = CVOutputParser.read_est_obs_file(ext_est_file)
        #heu_est = CVOutputParser.read_est_obs_file(heu_est_file)


        # Index 1 should hold the observed value parsed from the file
        # is the same mapped to every estimate, so hust read it once.
        #obs = max_ent_est[triple][1]

        # maxent estimate
        est = max_ent_est[triple][0]
        maxent_estimates[int(round(est, 0))] += 1
        # extrapolation estimate
        est2 = ext_est[triple][0]
        ext_est[int(round(est2, 0))] += 1
        # # independence estimat?

        # heurestic, use max_ent for 0 triple in sample
        #est4 = heu_est[triple][0]

        # Index 2 should hold the pair triple ratio.
        # is the sam for every estimat
        ratio = max_ent_est[triple][2]
        accumulated_ratio = accumulated_ratio + ratio
        # add errors to the ratio bin
        number_of_measurements += 1

        iteration += 1

    print 'values binned: ', values_binned
    print max_ent_ratio_error
    print ext_ratio_error
    avg_ratio = accumulated_ratio/iteration
    print 'average ratio: ', avg_ratio
    # interpolate(max_ent_ratio_error)
    # interpolate(ext_ratio_error)

    scatter(maxent_estimates.keys(), maxent_estimates.values(), color='blue')
    plot(ext_est.keys(), ext_est.values(), color='red')

