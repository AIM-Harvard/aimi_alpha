from ModelRunnerConfig import ModelRunnerConfig, DataHandler
from DataSorter import DataSorter
from DataConverter import NiftiConverter

# clean
import shutil
shutil.rmtree("/app/data/sorted", ignore_errors=True)
shutil.rmtree("/app/data/nifti", ignore_errors=True)

# config
config = ModelRunnerConfig()
config.makeDirs()

# sort
DataSorter(config).execute()

# converter
NiftiConverter(config).execute()
