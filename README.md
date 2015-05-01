saas2014
========

# algorithm seminar project

To run e.g. cross validation on the AOL data.
Add env.py to the src/ directory, this file is
ignored by git, and should point to your local
data files, e.g. for the AOL data. See env_example.py
for an example.

Then:
from parsers import AOLParser
import env
trans = AOLParser.parse_aol_to_mat(env.AOL_PATH)

