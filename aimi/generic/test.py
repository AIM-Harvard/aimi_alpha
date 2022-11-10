from Config import Config, DataType, FileType
from generic.modules.sorter.DataSorter import DataSorter
from modules.convert.NiftiConverter import NiftiConverter
from modules.convert.DsegConverter import DsegConverter
from generic.modules.organizer.DataOrganizer import DataOrganizer
from generic.modules.filter.DataFilter import SIDFilter
from generic.modules.runner.ModelRunner import TotalSegmentatorRunner

# clean up
import shutil
shutil.rmtree("/app/data/sorted", ignore_errors=True)               # output of dicomsort
shutil.rmtree("/app/tmp", ignore_errors=True)                       # model data is stored here 
shutil.rmtree("/app/mymodeldata/allnifti", ignore_errors=True)      # created by organizer test
shutil.rmtree("/app/data/output_data", ignore_errors=True)          # final output

# dev helper
def printSectionHeader(title: str, l=40):
    d = "-" * max(0, l - len(title))
    n = printSectionHeader.n + 1
    printSectionHeader.n = n
    print(f"\n {n:<2} - {title} {d}")
printSectionHeader.n = 0

def printInstanceOverview(config):
    print("\nInstances: ")
    for i in config.data.instances:
        print(str(i))
        for d in i.data:
            print("> ", str(d))
        print()

# config
config = Config()
config.makeDirs()

for instance in config.data.instances: print(str(instance))

# - sorter ------------------------------
printSectionHeader("SORT")

sorter = DataSorter(config)
sorter.execute()

printInstanceOverview(config)

# - filter ------------------------------
printSectionHeader("FILTER")

filter = SIDFilter(config)
filter.sid = "1.3.6.1.4.1.14519.5.2.1.7009.9004.209031079770197083919717286861"
filter.execute()

printInstanceOverview(config)

# - converter ---------------------------
printSectionHeader("CONVERTER")

converter = NiftiConverter(config)
converter.execute()

printInstanceOverview(config)


# - organizer ---------------------------
printSectionHeader("ORGANIZE")

organizer = DataOrganizer(config)
organizer.setTarget(type=DataType(FileType.NIFTI), dir="/app/mymodeldata/allnifti")
organizer.execute()

printInstanceOverview(config)

# - model runner ------------------------
printSectionHeader("RUN MODEL")

modelrunner = TotalSegmentatorRunner(config)
modelrunner.execute()

printInstanceOverview(config)

# - dicomseg export ---------------------
printSectionHeader("DICOMSEG")

converter = DsegConverter(config)
converter.execute()

printInstanceOverview(config)

# - done --------------------------------
print("X - DONE ------------")

# export datahandler
import pickle
with open('/app/datahandler.pickle', 'wb') as f:
    pickle.dump(config.data, f)

print("> exported data handler as /app/datahandler.pickle")