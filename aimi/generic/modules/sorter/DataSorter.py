import os
import subprocess

from aimi.generic.Config import Module, UnsortedInstance, SortedInstance, InstanceData, DataType, FileType, CT

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
        schema = str(self.c['base_dir']) + "/" + str(self.c['structure'])
        self.v("sorting schema:",  schema)

        # create output folder if required
        if not os.path.isdir(self.c['base_dir']):
            os.makedirs(self.c['base_dir'])

        # compose command
        bash_command = [
            "dicomsort", 
            "-k", "-u",
            str(instance.abspath), 
            schema
        ]

        bash_return = subprocess.run(bash_command, check=True, text=True)

    def getSeriesIDs(self):
        return os.listdir(self.c['base_dir'])

    def task(self) -> None:

        # run dicomsort
        self.sort() 
        
        # create data instances based on the sorted output
        instances = []
        for sid in self.getSeriesIDs():
            inst = SortedInstance(os.path.join("sorted", sid))
            inst.data = [InstanceData("dicom", DataType(FileType.DICOM, CT))] # TODO: dynamic meta (CT ofc cannot be hardcoded!)
            inst.attr['SeriesID'] = sid # TODO: also not ready for productive use 
            instances.append(inst)

        # update instances to the global data handler
        self.config.data.instances = instances
