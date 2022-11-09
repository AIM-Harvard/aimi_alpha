from Config import Config, Sequence
from DataSorter import DataSorter
from modules.convert.NiftiConverter import NiftiConverter
from modules.convert.DsegConverter import DsegConverter
from ModelRunner import TotalSegmentatorRunner

# clean
import shutil
shutil.rmtree("/app/data/sorted", ignore_errors=True)
shutil.rmtree("/app/data/nifti", ignore_errors=True)
shutil.rmtree("/app/tmp", ignore_errors=True)
shutil.rmtree("/app/data/output_data", ignore_errors=True)

# config
config = Config()
config.makeDirs()
config.verbose = False  # TODO: define levels of verbosity and integrate consistently. 

# run script
Sequence(config, modules=[
    DataSorter,
    NiftiConverter,
    TotalSegmentatorRunner,
    DsegConverter
])