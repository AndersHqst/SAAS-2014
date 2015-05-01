
class CVOutputParser():

    @classmethod
    def read_est_obs_file(self, tsv_filename):
        """
        Reads the result data file from running Cross Validation.
        Returns dictionary with triples and their given (estimates, observations)
        for the triple in the sample.
        """
        d = {}
        for index, line in enumerate(open(tsv_filename, 'rb')):
            chunks = line.replace('\n', '').split('\t')
            if index == 0:
                n1_pos = chunks.index('n1')
                n2_pos = chunks.index('n2')
                n3_pos = chunks.index('n3')
                
                s1_pos = chunks.index('s1')
                s2_pos = chunks.index('s2')
                s3_pos = chunks.index('s3')
                s12_pos = chunks.index('s12')
                s13_pos = chunks.index('s13')
                s23_pos = chunks.index('s23')
                s123_pos = chunks.index('s123')

                est_pos = chunks.index('est')
                obs_pos = chunks.index('obs')
                ratio_pos = chunks.index('pair_trip_ratio')
            else:
                triangle = (int(chunks[s1_pos]), int(chunks[s2_pos]), int(chunks[s3_pos]), int(chunks[s12_pos]), int(chunks[s13_pos]), int(chunks[s23_pos]), int(chunks[s123_pos]))
                d[(chunks[n1_pos], chunks[n2_pos], chunks[n3_pos])] = (float(chunks[est_pos]), float(chunks[obs_pos]), float(chunks[ratio_pos]), triangle)

        return d

    @classmethod
    def read_est_obs_file_disc_version(self, tsv_filename):
        """
        Reads the result data file from running Cross Validation, returning a line at the
        from the tsv_file.
        """
        for index, line in enumerate(open(tsv_filename, 'rb')):
            chunks = line.replace('\n', '').split('\t')
            if index == 0:
                n1_pos = chunks.index('n1')
                n2_pos = chunks.index('n2')
                n3_pos = chunks.index('n3')
                
                s1_pos = chunks.index('s1')
                s2_pos = chunks.index('s2')
                s3_pos = chunks.index('s3')
                s12_pos = chunks.index('s12')
                s13_pos = chunks.index('s13')
                s23_pos = chunks.index('s23')
                s123_pos = chunks.index('s123')

                est_pos = chunks.index('est')
                obs_pos = chunks.index('obs')
                ratio_pos = chunks.index('pair_trip_ratio')
            else:
                triangle = (int(chunks[s1_pos]), int(chunks[s2_pos]), int(chunks[s3_pos]), int(chunks[s12_pos]), int(chunks[s13_pos]), int(chunks[s23_pos]), int(chunks[s123_pos]))
                yield (float(chunks[est_pos]), float(chunks[obs_pos]), float(chunks[ratio_pos]), triangle)


    @classmethod
    def read_est_obs_file_disc_version_2(self, tsv_filename):
        """
        Reads the result data file from running Cross Validation, returning a line at the
        from the tsv_file.

        Version 2 also returns the actual items
        """
        for index, line in enumerate(open(tsv_filename, 'rb')):
            chunks = line.replace('\n', '').replace('\r', '').split('\t')
            if index == 0:
                n1_pos = chunks.index('n1')
                n2_pos = chunks.index('n2')
                n3_pos = chunks.index('n3')
                
                s1_pos = chunks.index('s1')
                s2_pos = chunks.index('s2')
                s3_pos = chunks.index('s3')
                s12_pos = chunks.index('s12')
                s13_pos = chunks.index('s13')
                s23_pos = chunks.index('s23')
                s123_pos = chunks.index('s123')

                est_pos = chunks.index('est')
                obs_pos = chunks.index('obs')
                ratio_pos = chunks.index('pair_trip_ratio')
            else:
                triangle = (int(chunks[s1_pos]), int(chunks[s2_pos]), int(chunks[s3_pos]), int(chunks[s12_pos]), int(chunks[s13_pos]), int(chunks[s23_pos]), int(chunks[s123_pos]))
                yield (chunks[n1_pos], chunks[n2_pos], chunks[n3_pos]), (float(chunks[est_pos]), float(chunks[obs_pos]), float(chunks[ratio_pos]), triangle)


    @classmethod
    def read_merged_file_disc_version(self, tsv_filename):
        """
        Reads the result data file from running Cross Validation, returning a line at the
        from the tsv_file.

        Version 2 also returns the actual items
        """
        for index, line in enumerate(open(tsv_filename, 'rb')):
            chunks = line.replace('\n', '').split('\t')
            if index == 0:
                n1_pos = chunks.index('n1')
                n2_pos = chunks.index('n2')
                n3_pos = chunks.index('n3')
                
                s1_pos = chunks.index('s1')
                s2_pos = chunks.index('s2')
                s3_pos = chunks.index('s3')
                s12_pos = chunks.index('s12')
                s13_pos = chunks.index('s13')
                s23_pos = chunks.index('s23')
                s123_pos = chunks.index('s123')

                maxent_pos = chunks.index('est')
                ext_pos = chunks.index('ext')
                obs_pos = chunks.index('obs')
                ratio_pos = chunks.index('pair_trip_ratio')
            else:
                triangle = (int(chunks[s1_pos]), int(chunks[s2_pos]), int(chunks[s3_pos]), int(chunks[s12_pos]), int(chunks[s13_pos]), int(chunks[s23_pos]), int(chunks[s123_pos]))
                yield (chunks[n1_pos], chunks[n2_pos], chunks[n3_pos]), (float(chunks[maxent_pos]), float(chunks[ext_pos]), float(chunks[obs_pos]), float(chunks[ratio_pos]), triangle)


    @classmethod
    def read_merged_file(self, tsv_filename):
        """
        Reads the result data file from running Cross Validation, returning a line at the
        from the tsv_file.

        Version 2 also returns the actual items
        """
        d = {}
        for index, line in enumerate(open(tsv_filename, 'rb')):
            chunks = line.replace('\n', '').split('\t')
            if index == 0:
                n1_pos = chunks.index('n1')
                n2_pos = chunks.index('n2')
                n3_pos = chunks.index('n3')
                
                s1_pos = chunks.index('s1')
                s2_pos = chunks.index('s2')
                s3_pos = chunks.index('s3')
                s12_pos = chunks.index('s12')
                s13_pos = chunks.index('s13')
                s23_pos = chunks.index('s23')
                s123_pos = chunks.index('s123')

                maxent_pos = chunks.index('est')
                ext_pos = chunks.index('ext')
                obs_pos = chunks.index('obs')
                ratio_pos = chunks.index('pair_trip_ratio')
            else:
                triangle = (int(chunks[s1_pos]), int(chunks[s2_pos]), int(chunks[s3_pos]), int(chunks[s12_pos]), int(chunks[s13_pos]), int(chunks[s23_pos]), int(chunks[s123_pos]))
                d[((chunks[n1_pos], chunks[n2_pos], chunks[n3_pos]), index)] = (float(chunks[maxent_pos]), float(chunks[ext_pos]), float(chunks[obs_pos]), float(chunks[ratio_pos]), triangle)
        return d  

