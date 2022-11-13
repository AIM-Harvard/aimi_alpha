"""
-------------------------------------------------
AIMI beta - Data Organizer Module
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""

from typing import Dict, Optional
import os, shutil, uuid, re
from aimi.generic.Config import Config, Module, Instance, InstanceData, DataType, FileType

class DataOrganizer(Module):
    target: Dict[DataType, str] = {}

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.dry = False

    def setTarget(self, type: DataType, dir: str) -> None: # TODO: define copy / move action
        """
        Target directory where files of matching data type are copied to.
        Absolute path required. 
        Dynamic options:
            [random] -> random uuid4 string
            [path] -> relative path of the datatype (<DataType>.path)
            [i:id] -> instance id
            [i:...] -> any attribute from instance id (<Instance>.attr[...])
            [d:...] -> any metadata from datatype (<DataType>.meta[...])
        """
        self.target[type] = dir

    def task(self) -> None:
        for instance in self.config.data.instances:
            self.organize(instance)

    def resolveTarget(self, target: str, data: InstanceData) -> Optional[str]:
        vars = re.findall("\[(i:|d:)?([\w]+)\]", target)
        print("vars: ", vars)

        if len(vars) == 0:
            return target
        else:
            _target = target
            for scope, var in vars:
                if scope == "":
                    if var == "random":
                        _target = _target.replace('[random]', str(uuid.uuid4()))
                    elif var == "path":
                        _target = _target.replace("[path]", data.path)
                elif scope == "i:":
                    if not var in data.instance.attr:
                        print(f"WARNING: attribute '{var}' missing in instance {data.instance}. Case ignored.")
                        return None
                    _target = _target.replace('[' + scope + var + ']', data.instance.attr[var])
                elif scope == "d:":
                    if not var in data.type.meta:
                        print(f"WARNING: key '{var}' missing in datatype {data.type}. Case ignored.")
                        return None
                    _target = _target.replace('[' + scope + var + ']', data.type.meta[var])
                else:
                    raise ValueError(f"Unresolved pattern: '{scope}:{var}' in {target}.")

            return _target

    def organize(self, instance: Instance) -> None:
        
        print("organizing instance", str(instance))
        
        for (type, target) in self.target.items():
            
            if not instance.hasType(type):
                print(f"type {str(type)} not in instance. all types are:")
                for d in instance.data:
                    print("> ", str(d.type), d.abspath)
                continue

            # get input file path
            inp_datas = instance.filterData(type)
            for inp_data in inp_datas:

                inp_data_target = self.resolveTarget(target, inp_data)
                if not inp_data_target:
                    continue                

                # create target directory if required
                inp_data_target_dir = os.path.dirname(inp_data_target)
                if not self.dry and not os.path.isdir(inp_data_target_dir):
                    os.makedirs(inp_data_target_dir)
                    self.v(f"created directory {inp_data_target_dir}")

                # add to instance
                # TODO: the data is now outside of our managed file structure but should still be linked to the instance. For now, just set the base path. However, this will cause type duplications thus not yet compatible with conversion modules applied afterwards. However, we've to decide if we enforce all conversion steps to only operate on our internal data structure.
                out_data = InstanceData(inp_data_target, type)
                out_data.base = ""
                instance.addData(out_data) # TODO: either remove dry mode or handle 

                # copy
                if not self.dry:
                    shutil.copyfile(inp_data.abspath, out_data.abspath)
                else:
                    print(f"dry copy {inp_data.abspath} to {out_data.abspath}")

                