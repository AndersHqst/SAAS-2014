def triple_errors(output_folder, triple):
    from parsers import CVOutputParser
    from utils import interpolate, avg, confidence_interval
    import math
    from collections import Counter
    import os
    """ 
    Plot accumulated errors for estimators against pair triple ratios.
    Ratios are binned in the range 0.0 to 1.0.
    """
    if not output_folder[-1] == '/':
        output_folder += '/'

    iteration = -1
    max_ent_errors = []
    ext_errors = []
    max_ent_abs_errors = []
    ext_abs_errors = []
    samples_ignored = 0
    while True:
        iteration += 1
        max_ent_est_file = output_folder + str(iteration) + '_data.tsv'
        ext_est_file = output_folder + str(iteration) + '_data_extrapolation.tsv'
        # heu_est_file = output_folder + str(iteration) + '_data_heurestic.tsv'
        # read baseline also?
        # Read until we do not find an output file
        if not os.path.exists(max_ent_est_file):
            break

        # Read the maxent estimate
        found = False
        for sample_triple, (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version_2(max_ent_est_file):
            (s1, s2, s3, s12, s13, s23, s123) = triangle

            if sample_triple == triple:
                # if s123 == 0:
                #     break
                found = True
                max_ent_errors.append(est-obs)
                max_ent_abs_errors.append(abs(obs-est))
                break

        if not found:
            samples_ignored += 1
            continue

        for sample_triple, (est, obs, ratio, triangle) in CVOutputParser.read_est_obs_file_disc_version_2(ext_est_file):
            (s1, s2, s3, s12, s13, s23, s123) = triangle

            if sample_triple == triple:
                ext_errors.append(est-obs)
                ext_abs_errors.append(abs(obs-est))
                break

    # maxent confidence interval
    maxent_ci = confidence_interval(max_ent_errors)
    # extrapolation confidence interval
    ext_ci = confidence_interval(ext_errors)

    print 'samples ignored: ', samples_ignored
    print 'maxent avg error: ', round(avg(max_ent_errors),1)
    print 'maxent 95% confidence interval: ', (round(maxent_ci[0],1), round(maxent_ci[1],2))
    print 'extrapolation avg error: ', round(avg(ext_errors),1)
    print 'extrapolation 95% confidence interval: ', (round(ext_ci[0],1), round(ext_ci[1],2))

    # round
    max_ent_errors_rounded = [round(x,1) for x in max_ent_errors]
    ext_errors_rounded = [round(x,1) for x in ext_errors]

    # plot
    xlabel('Estimate error')
    ylabel('Bucket size')
    # text(0.1, 0.8, 'Maxent')
    # text(0.1, 0.7, 'avg. error: ' + str(avg(max_ent_errors)))
    # text(0.1, 0.6, '95% conf. interval: ' + str(maxent_ci))

    # text(0.5, 0.8, 'Extrapolation')
    # text(0.5, 0.7, 'avg. error: ' + str(avg(ext_errors)))
    # text(0.5, 0.6, '95% conf. interval: ' + str(ext_ci))

    hist([max_ent_errors_rounded, ext_errors_rounded], color=('b', 'r'))
    
    return max_ent_errors, max_ent_abs_errors, ext_errors, ext_abs_errors

