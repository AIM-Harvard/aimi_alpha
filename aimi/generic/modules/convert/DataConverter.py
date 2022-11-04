from typing import Optional
from Config import Module, Instance, InstanceData, DataType, FileType

class DataConverter(Module):
    """
    Conversion module. 
    Convert instance data from one to another datatype without modifying the data.
    """

    # TODO: Idea: We could have InstancData as (optional) return type for convert

    def convert(self, instance: Instance) -> None: #-> Optional[InstanceData]:
        print("Ooops, not implemented.")
        #return None

    def task(self):
        # get instances
        instances = self.config.data.getInstances(True, DataType(FileType.DICOM))
        assert len(instances) > 0

        # execute convert for each instance
        # TODO: add parallelization
        for instance in instances:
            converted = self.convert(instance)

            if converted is not None:
                instance.addData(converted)
