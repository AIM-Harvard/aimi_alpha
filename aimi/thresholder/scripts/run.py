"""
    -------------------------------------------------
    AIMI beta - Apply a simple thresholding operation 
                to an input image for testing.
    -------------------------------------------------
    
    -------------------------------------------------
    Author: Leonard Nürnberg
    Email:  leonard.nuernberg@maastrichtuniversity.nl
    -------------------------------------------------
"""

import sys, os
sys.path.append('.')

from aimi.generic.Config import Config, DataType, FileType, CT, SEG
from aimi.generic.modules.importer.NrrdImporter import NrrdImporter
from aimi.generic.modules.organizer.DataOrganizer import DataOrganizer
from aimi.thresholder.utils.ThresholdingRunner import ThresholdingRunner

# clean-up
#import shutil
#shutil.rmtree("/app/data/sorted", ignore_errors=True)
#shutil.rmtree("/app/data/nifti", ignore_errors=True)
#shutil.rmtree("/app/tmp", ignore_errors=True)
#shutil.rmtree("/app/data/output_data", ignore_errors=True) # <-- we use in = out so not a good idea :D

# config
config = Config('/app/aimi/thresholder/config/config.yml')
config.verbose = True  # TODO: define levels of verbosity and integrate consistently. 

# convert (ct:dicom -> ct:nrrd)
NrrdImporter(config).execute()

# execute model (ct:nifti -> seg:nifti)
ThresholdingRunner(config).execute()

# organize data into output folder
organizer = DataOrganizer(config)
organizer.setTarget(DataType(FileType.NRRD, SEG), "/app/data/output_data/output.nrrd")
organizer.execute()