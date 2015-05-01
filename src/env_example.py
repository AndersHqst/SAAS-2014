import os 

# Build paths with this: os.path.join(BASE_DIR, 'path to relevant data')
# where base dir is the src/ folder
BASE_DIR = os.path.abspath('.')

# AOL files.
AOL_PATH = os.path.join(BASE_DIR, '../../data/infochimps_aol-search-data/AOL-user-ct-collection/')
AOL_MERGED_FILE = '/Users/ahkj/dev/SAAS/data/infochimps_aol-search-data/AOL-user-ct-collection/all_aol.tab'
AOL_100k = '/Users/ahkj/dev/SAAS/data/infochimps_aol-search-data/AOL-user-ct-collection/all_aol_100k.tab'
AOL_1M = '/Users/ahkj/dev/SAAS/data/infochimps_aol-search-data/AOL-user-ct-collection/all_aol_1M.tab'

# Frequent items file, output created from running Borgelt from the command line
BORGELT_AOL_FREQUENT_ITEMS = os.path.join(BASE_DIR, '../../data/aol/frequent_items_aol_supp_30.tab')
# Algorithm to use with disc based cross validation
BORGELT_ALGORITHM = '/Users/ahkj/dev/SAAS/borgelt/fpgrowth/fpgrowth/src/fpgrowth'

TEST_TAB = os.path.join(BASE_DIR, '../../data/test3.tab')

# Random data file created with the utils.random_generator
RANDOM_DATA = os.path.join(BASE_DIR, '../../data/random_data.tab')
