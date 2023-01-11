import os

from aimi.generic.Config import UnsortedInstance, InstanceData, DataType, FileType, CT
from aimi.generic.modules.importer.DataImporter import DataImporter

class NrrdImporter(DataImporter):

    def task(self) -> None:
        # NOTE: completely bypassing DataImporter here. Needs review and specification.

        # input nrrd file name
        input_file_name = self.c['input_file_name']
        self.v("importing", input_file_name)

        # create instance
        instance = UnsortedInstance("input_data")
        dtype = DataType(FileType.NRRD, CT)
        data = InstanceData(input_file_name, dtype)
        instance.addData(data)

        # set instance as the only imported instance
        self.config.data.instances = [instance]