from Config import Config
from modules.convert.DsegConverter import DsegConverter
import shutil

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

# clean up
import shutil
shutil.rmtree("/app/data/output_data", ignore_errors=True)               # final output

# config
config = Config()
config.makeDirs()

# load intermediate progress from pickle (just the datahandler)
import pickle
with open('/app/datahandler.pickle', 'rb') as f:
    config.data = pickle.load(f)

# what do we have?
printInstanceOverview(config)

# convert to dicomseg
converter = DsegConverter(config)
converter.execute()

# just expose it all
shutil.copytree("/app/data/sorted/", "/app/data/output_data/sorted/")