"""
    -------------------------------------------------
    AIMI beta - Slicer run of the Totalsegmentator
      pipeline
    -------------------------------------------------
    
    -------------------------------------------------
    Author: Dennis Bontempi
    Email:  dbontempi@bwh.harvard.edu
    -------------------------------------------------
"""

import sys, os
sys.path.append('.')

from aimi.generic.Config import Config, DataType, FileType, CT, SEG
from aimi.generic.modules.importer.NrrdImporter import NrrdImporter
from aimi.generic.modules.convert.NiftiConverter import NiftiConverter
from aimi.generic.modules.organizer.DataOrganizer import DataOrganizer
from aimi.totalsegmentator.utils.TotalSegmentatorRunner import TotalSegmentatorRunner

# config
config = Config('/app/aimi/totalsegmentator/config/slicer_config.yml')
config.verbose = True  # TODO: define levels of verbosity and integrate consistently. 

# load NRRD file (ct:nrrd)
NrrdImporter(config).execute()

# convert (ct:nrrd -> ct:nifti)
NiftiConverter(config).execute()

# execute model (ct:nifti -> seg:nifti)
TotalSegmentatorRunner(config).execute()

# organize data into output folder
organizer = DataOrganizer(config)
organizer.setTarget(DataType(FileType.NIFTI, SEG), "/app/data/output_data/[d:roi].nii.gz")
organizer.execute()