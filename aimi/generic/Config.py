import os, time, uuid, itertools
from enum import Enum
from typing import List, Dict, Union, Optional

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

    def __init__(self, ftype: FileType, meta: Optional[Dict[str, str]] = None) -> None:
        self.ftype: FileType = ftype
        self.meta: Dict[str, str] = meta if meta else {}

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
        self._data: List['InstanceData'] = []

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

    def getDataMetaKeys(self) -> List[str]:
        return list(set(sum([list(d.type.meta.keys()) for d in self.data], [])))

    def printDataMetaOverview(self, datas: Optional[List['InstanceData']] = None, metaKeys: Optional[List[str]] = None, compress: bool = True, label: str = "") -> None:

        # you may specify data explicitly (e.g. the result of a filter), otherwise we use the instance's data
        if not datas:
            datas = self.data
        
        # if not specified use all
        if not metaKeys:
            metaKeys = self.getDataMetaKeys()
        
        # count
        cnt: Dict[FileType, Dict[str, Dict[str, int]]] = {}
        cnt_ftype: Dict[FileType, int] = {}

        for data in datas:

            # count filetypes (regardless of meta presence)
            if not data.type.ftype in cnt_ftype: cnt_ftype[data.type.ftype] = 0
            cnt_ftype[data.type.ftype] += 1

            # count meta 
            for k, v in data.type.meta.items():
                if not data.type.ftype in cnt: cnt[data.type.ftype] = {}
                if not k in cnt[data.type.ftype]: cnt[data.type.ftype][k] = {}
                if not v in cnt[data.type.ftype][k]: cnt[data.type.ftype][k][v] = 0

                cnt[data.type.ftype][k][v] += 1

        # formatting options
        # TODO: outsource or standardize if used frequently
        chead = '\033[95m'
        cyan = '\033[96m'
        cend = '\033[0m'
        fitalics = '\x1B[3m'
        fnormal ='\x1B[0m'

        # print fromatted output
        print(f". {fitalics}{label}{fnormal}")
        for ftype in cnt:
            print(f"├── {chead}{str(ftype)}{cend} [{cnt_ftype[ftype]}]")
            for k in cnt[ftype]:
                print(f"|   ├── {cyan}{k:<20}{cend}")
                for v, n in cnt[ftype][k].items():
                    if not compress or n > 1:
                        print(f"|   |   ├── ({n:<4}) {cyan}{v}{cend}")
                if compress:
                    n1lst = sorted([v for v, n in cnt[ftype][k].items() if n == 1])

                    if n1lst:
                        print(f"|   |   ├── ", end="")
                        
                        while n1lst:
                            cc = 12
                            while n1lst and cc + len(n1lst[0]) + 2 < os.get_terminal_size().columns:
                                print(n1lst[0] + ", ", end="")
                                cc  += len(n1lst[0]) + 2
                                n1lst = n1lst[1:]
                            if n1lst:
                                print(f"\n|   |   |   ", end="")
                        print("")

    def filterData(self, ref_types: Union[DataType, List[DataType]], metaKeys: Optional[List[str]] = None) -> List['InstanceData']:
        if not isinstance(ref_types, list):
            ref_types = [ref_types]
        return list(set(sum([self._filterData(ref_type, metaKeys) for ref_type in ref_types], [])))       

    def _filterData(self, ref_type: DataType, metaKeys: Optional[List[str]] = None) -> List['InstanceData']: 
        """
        Filter for instance data by a reference data type. Only instance data that match the file type and specified meta data of the reference type are returned. A datatype matches the reference type, if all metadata of the reference type is equal to the datatype. If a datatype contains additional meta data compared to the reference type (specialization) those additional keys are ignored. The keys of the reference type that are used for comparison can be limited to those explicitl mentionened using the metaKeys list (all meta keys of the reference type are used if metaKeys is empty).
        """

        if not metaKeys:
            metaKeys = []

        # check that requested metakeys occur at least once in (any) instance data
        # filtering for missing meta keys is not really an issue but in most cases a hint that something went wrong. 
        # TODO: propagate and collect warnings to the config, allow for verbosity settings and (exported) reports
        mks = self.getDataMetaKeys()
        if not all([k in mks for k in metaKeys]):
            print("warning: meta key does not exist on this data.")

        # check that the metakeys used for filtering occur on the reference type (ref_type)
        # here we use a breaking assertion since reference type and requested filters should always match.
        # This might be revisited for dynamic situations having metaKeys as a general (instead of an individual) limitation.
        assert all([k in ref_type.meta.keys() for k in metaKeys]), f"Meta keys ({', '.join(metaKeys)}) don't match the reference type's meta keys ({', '.join(ref_type.meta.keys())})."

        # collect only instance data passing all checks (ftype, meta)
        matching_data: List[InstanceData] = []

        # iterate all instance data of this instance
        for data in self.data:
            # check file type, ignore other filetypes
            if data.type.ftype != ref_type.ftype:
                continue

            # check meta, ignore some keys
            meta_check_pass: bool = True
            for k in ref_type.meta.keys():

                # if applicable, ignore keys not set explicitly
                if metaKeys and k not in metaKeys:
                    print("ignore not set key")
                    continue

                # check value match
                if data.type.getMeta(k) != ref_type.getMeta(k):
                    meta_check_pass = False
                    break

            # ignore instance data that failed the meta check
            if not meta_check_pass:
                continue

            # add instance data that passes all prior checks
            matching_data.append(data)

        # return matches
        return matching_data

    def getData(self, ref_types: Union[DataType, List[DataType]], metaKeys: Optional[List[str]] = None) -> 'InstanceData':
        fdata = self.filterData(ref_types, metaKeys)

        # warning if multiple data available
        if len(fdata) > 1: 
            print("Warning, type is not unique. First element is returned.")
        
        #FIXME: when adding assertions, this should throw
        if len(fdata) == 0: 
            print("Ooops, no data found.")
            print("> You were asking for " + str(type) + ". But all I have is:")
            print("> ", "\n> ".join([str(x) for x in self.data]))

        # return data
        return fdata[0]

    # TODO: make it possible to connect data and instance such that all paths are calculatedd correctly but the data is "invisible" to the instance (at salvo). Invoke a .complete() method to resolve. Technically, this can already be achived (although not as obvious to the reader) by first assigning th einstance to the data (data.instance = instance) but without adding th edata to the instance (which has to be done later a.k.a. resolving). We could, however, check if data has a diverging instance and in that case forbid adding (assert data.instance is None or self)
    # e.g. add , salvo: bool = False to addData signature
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