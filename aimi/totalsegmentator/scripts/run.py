"""
    -------------------------------------------------
    AIMI beta - run the TS pipeline locally
    -------------------------------------------------
    
    -------------------------------------------------
    Author: Leonard Nürnberg
    Email:  leonard.nuernberg@maastrichtuniversity.nl
    -------------------------------------------------
"""

import sys, os
sys.path.append('.')

from aimi.generic.Config import Config, DataType, FileType, CT, SEG
from aimi.generic.modules.importer.DataSorter import DataSorter
from aimi.generic.modules.convert.NiftiConverter import NiftiConverter
from aimi.generic.modules.convert.DsegConverter import DsegConverter
from aimi.generic.modules.organizer.DataOrganizer import DataOrganizer
from aimi.totalsegmentator.utils.TotalSegmentatorRunner import TotalSegmentatorRunner

# clean
import shutil
shutil.rmtree("/app/data/sorted", ignore_errors=True)
shutil.rmtree("/app/data/nifti", ignore_errors=True)
shutil.rmtree("/app/tmp", ignore_errors=True)
shutil.rmtree("/app/data/output_data", ignore_errors=True)

# config
config = Config('/app/aimi/totalsegmentator/config/config.yml')
config.verbose = True  # TODO: define levels of verbosity and integrate consistently. 

# sort
DataSorter(config).execute()

# convert (ct:dicom -> ct:nifti)
NiftiConverter(config).execute()

# execute model (ct:nifti -> seg:nifti)
TotalSegmentatorRunner(config).execute()

# export datahandler
import pickle
with open('/app/datahandler.pickle', 'wb') as f:
    pickle.dump(config.data, f)
print("stored data handler at /app/datahandler.pickle")

# convert (seg:nifti -> seg:dicomseg)
DsegConverter(config).execute()

# organize data into output folder
organizer = DataOrganizer(config)
organizer.setTarget(DataType(FileType.NIFTI, CT), "/app/data/output_data/[i:SeriesID]/[path]")
organizer.setTarget(DataType(FileType.DICOMSEG, SEG), "/app/data/output_data/[i:SeriesID]/TotalSegmentator.seg.dcm")
organizer.execute()