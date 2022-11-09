# TODO: remove sys hacks once in final (package-like) structure
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) 

# imports
from Config import Config, DataType, FileType, CT, SEG
from DataOrganizer import DataOrganizer

# clean up
import shutil
shutil.rmtree("/app/data/output_data", ignore_errors=True)               # final output

# config
config = Config('../config.yml')

# load intermediate progress from pickle (just the datahandler)
import pickle
with open('/app/datahandler.pickle', 'rb') as f:
    config.data = pickle.load(f)

#
organizer = DataOrganizer(config)
organizer.setTarget(DataType(FileType.NIFTI, CT), "/app/data/output_data/[i:SeriesID]/[path]")
organizer.setTarget(DataType(FileType.DICOMSEG, SEG), "/app/data/output_data/[i:SeriesID]/TotalSegmentator.seg.dcm")
organizer.execute()