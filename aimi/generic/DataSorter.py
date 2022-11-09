import os
import subprocess

from Config import Module, UnsortedInstance, SortedInstance, InstanceData, DataType, FileType, CT

class DataSorter(Module):
    """
    Sort Module.
    Organize patient data in a unique folder structure.
    For now, the static schema is: %SeriesInstanceUID/dicom/%SOPInstanceUID.dcm
    """

    def sort(self) -> None:       
        
        # sorter config
        # TODO: we should implement sth. like .getConfiguration(key) on the base module.
        #       but keep it simple for now, one change at a time 
        #   --> MAybe modules can define mandatory config keywords which can be checked at runtime
        c = self.config[self.__class__]

        # get input data
        instances = self.config.data.instances
        assert len(instances) == 1, "Error: too many instances. Sorter expxts a single instance."
        instance = instances[0]
        assert type(instance) == UnsortedInstance, "Error: instance must be unsorted."

        # print schema
        # TODO: config and integration of schema into folder struction ablation
        schema = str(c['base_dir']) + "/" + str(c['structure'])
        self.v("sorting schema:",  schema)

        # create output folder if required
        if not os.path.isdir(c['base_dir']):
            os.makedirs(c['base_dir'])

        # compose command
        bash_command = [
            "dicomsort", 
            "-k", "-u",
            str(instance.abspath), 
            schema
        ]

        bash_return = subprocess.run(bash_command, check=True, text=True)

    def getSeriesIDs(self):
        c = self.config[self.__class__]
        return os.listdir(c['base_dir'])

    def task(self) -> None:

        # run dicomsort
        self.sort() 
        
        # create data instances based on the sorted output
        instances = []
        for sid in self.getSeriesIDs():
            inst = SortedInstance(os.path.join("sorted", sid))
            inst.data = [InstanceData("dicom", DataType(FileType.DICOM, CT))] # TODO: dynamic meta (CT ofc cannot be hardcoded!)
            instances.append(inst)

        # update instances to the global data handler
        self.config.data.instances = instances
