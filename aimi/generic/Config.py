import os, time, uuid
from enum import Enum
from typing import List, Dict

class FileType(Enum):
    NONE = None
    NRRD = "nrrd"
    NIFTI = "nifti"
    DICOM = "dicom"
    DICOMSEG = "dicomseg"
    RTSTRUCT = "RTSTRUCT"

    def __str__(self) -> str:
        return self.name

#class DataSemantic:

class DataType:

    def __init__(self, ftype: FileType) -> None:
        self.ftype: FileType = ftype
        self.meta: Dict[str, str] = {}

    def getMeta(self, key: str) -> str:
        return self.meta[key] if key in self.meta else ""

    def setMeta(self, key: str, value: str) -> None:
        self.meta[key] = value

    def __str__(self) -> str:
        if not self.meta:
            return f"[T:{str(self.ftype)}]"
        else:
            uc = ":".join(["%s=%s"%(k, v) for k, v in self.meta.items()])
            return f"[T:{str(self.ftype)}:{uc}]"

class Instance: 
    handler: 'DataHandler'
    path: str
    _data: List['InstanceData']

    def __init__(self, path: str = "") -> None:
        self.path = path

    @property
    def abspath(self) -> str:
        return os.path.join(self.handler.base, self.path)

    @property
    def data(self) -> List['InstanceData']:
        return self._data

    @data.setter
    def data(self, data: List['InstanceData']):
        for d in data:
            d.instance = self
        self._data = data

    def hasType(self, type: DataType) -> bool:
        return len([d for d in self.data if d.type.ftype == type.ftype]) > 0 # FIXME: need proper matching!!! 

    def getDataByTypeAndMeta(self, type: DataType, metaKeys: List[str] = []): 
        d = []
        for d in self.data:
            # check  file type
            if d.type.ftype != type.ftype:
                continue

            # check all meta keys


    def getDataByType(self, type: DataType) -> 'InstanceData':
        d = [d for d in self.data if d.type.ftype == type.ftype] # FIXME: need proper matching!!! i.e. make DataType instances comparable (using = or isEqual filter ,ethod)

        # warning if multiple data available
        if len(d) > 1: 
            print("Warning, type is not unique. First element is returned.")
        
        #FIXME: when adding assertions, this should throw
        if len(d) == 0: 
            print("Ooops, no data found.")
            print("> You were asking for " + str(type) + ". But all I have is:")
            print("> ", "\n> ".join([str(x) for x in self.data]))

        # return data
        return d[0]

    def addData(self, data: 'InstanceData') -> None:
        data.instance = self
        self._data.append(data)

    def __str__(self) -> str:
        return "<I:%s>"%(self.abspath)

class InstanceData:
    instance: Instance
    type: DataType
    path: str
    base: str
    
    def __init__(self, path: str, type: DataType) -> None:
        self.path = path
        self.type = type

    @property
    def abspath(self) -> str:
        if hasattr(self, 'base'):
            return os.path.join(self.base, self.path)
        else:
            return os.path.join(self.instance.abspath, self.path)

    def __str__(self) -> str:
        srtd = "sorted" if isinstance(self.instance, SortedInstance) else "unsorted"
        return "<D:%s:%s:%s>"%(self.abspath, srtd, self.type)


class UnsortedInstance(Instance):
    def __init__(self, path: str = "") -> None:
        super().__init__(path)

class SortedInstance(Instance):
    def __init__(self, path: str = "") -> None:
        super().__init__(path)

class DataHandler:
    base: str
    _instances: List[Instance]

    def __init__(self, base) -> None:
        self.base = base
        self._instances = []

    @property
    def instances(self) -> List[Instance]:
       return self._instances

    @instances.setter
    def instances(self, instances: List[Instance]) -> None:
        for instance in instances:
            instance.handler = self
        self._instances = instances

    def getInstances(self, sorted: bool, type: DataType) -> List[Instance]:
        i_type = SortedInstance if sorted else UnsortedInstance
        return [i for i in self.instances if isinstance(i, i_type) and i.hasType(type)]

    def requestTempDir(self) -> str:
        abs_base = "/app/tmp"
        dir_name = str(uuid.uuid4())
        path  = os.path.join(abs_base, dir_name)

        # make path
        os.makedirs(path)

        # return
        return path

class Config:
    data: DataHandler

    # TODO: config will load it's dynamic, configurable attributes from yaml or json file. 
    # The config should be structured such that there is a shared config accessiblae to all modules and a (optional) config for each Module class. Class inheritance is followed naturally.

    def __init__(self) -> None:
        self.verbose = True

        self.sorted_structure = "%SeriesInstanceUID/dicom/%SOPInstanceUID.dcm"
        self.dicomseg_json_path = "/app/aimi/totalsegmentator/config/dicomseg_metadata_whole.json"
        self.data_base_dir = "/app/data"
        self.sorted_base_path = "/app/data/sorted"

        self.data = DataHandler(base=self.data_base_dir)
        self.data.instances = [
            UnsortedInstance("input_data")
        ]

    # NOTE: for develompemnt only
    def makeDirs(self):
        dirs_to_make = [
            self.sorted_base_path,
        ]

        for d in dirs_to_make:
            if not os.path.isdir(d):
                os.makedirs(name=d, mode=0o777)
                print('created directory ', d)
        
class Module:
    label: str
    config: Config

    def __init__(self, config: Config) -> None:
        self.label = self.__class__.__name__
        self.config = config
        self.verbose = config.verbose

    def v(self, *args) -> None:
        if self.verbose:
            print(*args)

    def execute(self) -> None:
        self.v("\n--------------------------")
        self.v("Start %s"%self.label)
        start_time = time.time()
        self.task()
        elapsed = time.time() - start_time
        self.v("Done in %g seconds."%elapsed)

    def task(self) -> None:
        """
        The task to execute on the module.
        This method needs to be overwriten in all module implementations.
        """
        print("Ooops, no task implemented in base module.")
        pass