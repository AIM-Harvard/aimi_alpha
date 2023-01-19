import os
from typing import Optional

from aimi.generic.Config import UnsortedInstance
from aimi.generic.modules.importer.DataImporter import DataImporter

class UnsortedInstanceImporter(DataImporter):

    def task(self) -> None:
        # NOTE: bypassing the base importer, as we do not import instance data but instead a shadow instance (of type UnsortedInstance) 
        # that points to a folder containing all unsorted dicom data.
        
        # get input dir from config
        input_dir = self.c['input_dir']
        
        # add unsorted instance
        self.config.data.instances = [
            UnsortedInstance(input_dir)
        ]  