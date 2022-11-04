from Config import Config
from DataSorter import DataSorter
from aimi.generic.modules.convert.DataConverter import NiftiConverter
from ModelRunner import TotalSegmentatorRunner

# clean
import shutil
shutil.rmtree("/app/data/sorted", ignore_errors=True)
shutil.rmtree("/app/data/nifti", ignore_errors=True)
shutil.rmtree("/app/tmp/model_out", ignore_errors=True)

# config
config = Config()
config.makeDirs()
config.verbose = False

# sort
DataSorter(config).execute()

# converter
NiftiConverter(config).execute()

# execute mdoel
TotalSegmentatorRunner(config).execute()