import sys; sys.path.append('.')

# imports
import os, yaml
from aimi.ymldicomseg import generateJsonMeta

yml_meta_file = os.path.join(os.path.dirname(__file__), '..', 'totalsegmentator', 'utils', 'meta.yml')
assert os.path.isfile(yml_meta_file)

# load yml meta
with open(yml_meta_file, 'r') as f:
    yml_meta = yaml.safe_load(f)

# generate json meta and file list
json_meta, seg_files = generateJsonMeta(yml_meta)

print(seg_files)
print(json_meta)