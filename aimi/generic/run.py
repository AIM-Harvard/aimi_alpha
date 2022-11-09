from Config import Config, DataType, FileType, CT, SEG
from DataSorter import DataSorter
from modules.convert.NiftiConverter import NiftiConverter
from modules.convert.DsegConverter import DsegConverter
from ModelRunner import TotalSegmentatorRunner
from DataOrganizer import DataOrganizer

# clean
import shutil
shutil.rmtree("/app/data/sorted", ignore_errors=True)
shutil.rmtree("/app/data/nifti", ignore_errors=True)
shutil.rmtree("/app/tmp", ignore_errors=True)
shutil.rmtree("/app/data/output_data", ignore_errors=True)

# config
config = Config('config.yml')
config.verbose = False  # TODO: define levels of verbosity and integrate consistently. 

# sort
DataSorter(config).execute()

# converter
NiftiConverter(config).execute()

# execute mdoel
TotalSegmentatorRunner(config).execute()

# convert to dicomseg
DsegConverter(config).execute()

# copy to output flder
organizer = DataOrganizer(config)
organizer.setTarget(DataType(FileType.NIFTI, CT), "/app/data/output_data/")
organizer.setTarget(DataType(FileType.DICOMSEG, SEG), "/app/data/output_data/totalsegmentator")
organizer.execute()