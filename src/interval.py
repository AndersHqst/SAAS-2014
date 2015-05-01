"""
Get and plot errors for triples in different frequency intervals.
"""

def plot_intervals(output_folder):
    from parsers import CVOutputParser
    from preprocessing import Preprocessor
    from utils import avg
    import os
    import math
    """ 
    Given a cross validation ouput. Certain triple intervals can be plottet
    to compare the error for extrapolation, max ent and the heurestic.
    
    The algorithm runs through each triple interval, and then for each sampled estiamte output
    the triples in the interval are looked up in each sample and the MAPE error is 
    recorded and the average errors are added. And the average of these averages
    are then plottet for each interval.

    """
    if not output_folder[-1] == '/':
        output_folder += '/'
    intervals = 30
    triple_intervals = Preprocessor.triple_intervals(output_folder + 'observed_frequent_items.out', intervals=intervals)

    avg_max_ent_errors = []
    avg_ext_errors = []
    avg_heu_errors = []
    pair_triple_ratios = [i/10. for i in range(11)] # binned ratios [0.0 to 1.0]
    max_ent_ratio_error = [0 for i in range(11)]
    ext_ratio_error = [0 for i in range(11)]

    for index, triple_interval in enumerate(triple_intervals):
        print 'Triple interval {} of {}'.format(index, intervals)
        iteration = 0
        MAPE_avg_errors = []
        MAPE_avg_errors_ext = []
        # MAPE_avg_errors_heu = []
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

            MAPE_errors = []
            MAPE_errors_ext = []
            # MAPE_errors_heu = []

            for triple in triple_interval:
                # Check that the triple has been estimated
                if triple in max_ent_est:

                    # Index 1 should hold the observed value parsed from the file
                    # is the same mapped to every estimate, so hust read it once.
                    obs = max_ent_est[triple][1]

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
                    # add errors to the ratio
                    max_ent_ratio_error[pair_triple_ratios.index(ratio_binned)] += abs(est-obs) / float(obs)
                    ext_ratio_error[pair_triple_ratios.index(ratio_binned)] += abs(est2-obs) / float(obs)


                    # MAPE error max ent
                    # error = abs(obs-est) #/ float(obs) * 100
                    # MAPE_errors.append(error)

                    # # MAPE error extrapolation
                    # error2 = abs(obs-est2) #/ float(obs) * 100
                    # MAPE_errors_ext.append(error2)

                    # MAPE error independence?

                    # MAPE error heurestic
                    # error4 = abs(obs-est4) #/ float(obs) * 100
                    # MAPE_errors_heu.append(error4)

                    

                    # MAPE baseline error?
            MAPE_avg_errors.append(avg(MAPE_errors))
            MAPE_avg_errors_ext.append(avg(MAPE_errors_ext))
            # MAPE_avg_errors_heu.append(avg(MAPE_errors_heu))
            iteration += 1

        avg_max_ent_errors.append(avg(MAPE_avg_errors))
        avg_ext_errors.append(avg(MAPE_avg_errors_ext))
        # avg_heu_errors.append(avg(MAPE_avg_errors_heu))
        

    plot(range(len(avg_max_ent_errors)), avg_max_ent_errors, color='blue')
    plot(range(len(avg_ext_errors)), avg_ext_errors, color='red')