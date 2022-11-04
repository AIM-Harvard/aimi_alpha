import re
from typing import List
from ModelRunnerConfig import Module, Instance, DataType

class DataFilter(Module):
    """
    Filter Module.
    Base implementation for filter operations.
    DEVNOTE: To simplify filter subclasses, a list of instances is passed to the generic filter function, making subclasses independand from the internally-global config and data handler instances.
    """
    
    def task(self) -> None:
        self.config.data.instances = self.filter(self.config.data.instances)

    def filter(self, instances: List[Instance]) -> List[Instance]:
        return instances

class TypeFilter(DataFilter):
    type: DataType

    def filter(self, instances: List[Instance]):
        return [i for i in instances if i.hasType(self.type)]


class SIDFilter(DataFilter):
    """
    For dev speedup only.
    """
    sid: str

    def getInstanceSid(self, instance: Instance) -> str:
        dicom_data = instance.getDataByType(DataType.DICOM)
        sid = dicom_data.abspath.split("/")[-2]
        print("ABS DICOM PATH: ", dicom_data.abspath, " | SID: ", sid)
        return sid

    def filter(self, instances: List[Instance]):
        return [i for i in instances if self.getInstanceSid(i) == self.sid]
