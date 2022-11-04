import os
import subprocess

from Config import Module, UnsortedInstance, SortedInstance, InstanceData, DataType

class DataSorter(Module):
    """
    Sort Module.
    Organize patient data in a unique folder structure.
    For now, the static schema is: %SeriesInstanceUID/dicom/%SOPInstanceUID.dcm
    """

    def sort(self) -> None:        
        # get input data
        instances = self.config.data.instances
        assert len(instances) == 1, "Error: too many instances. Sorter expxts a single instance."
        instance = instances[0]
        assert type(instance) == UnsortedInstance, "Error: instance must be unsorted."

        # print schema
        # TODO: config and integration of schema into folder struction ablation
        schema = str(self.config.sorted_base_path) + "/" + str(self.config.sorted_structure)
        self.v("sorting schema:",  schema)

        # compose command
        bash_command = [
            "dicomsort", 
            "-k", "-u",
            str(instance.abspath), 
            schema
        ]

        bash_return = subprocess.run(bash_command, check=True, text=True)

    def getSeriesIDs(self):
        return os.listdir(self.config.sorted_base_path)

    def task(self) -> None:

        # run dicomsort
        self.sort() 
        
        # create data instances based on the sorted output
        instances = []
        for sid in self.getSeriesIDs():
            inst = SortedInstance(os.path.join("sorted", sid))
            inst.data = [InstanceData("dicom", DataType.DICOM)]
            instances.append(inst)

        # update instances to the global data handler
        self.config.data.instances = instances
