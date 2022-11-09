from typing import Dict
import os, shutil, uuid
from Config import Module, Instance, InstanceData, DataType, FileType

class DataOrganizer(Module):
    target: Dict[DataType, str] = {}

    def setTarget(self, type: DataType, dir: str) -> None:
        self.target[type] = dir

    def task(self) -> None:
        for instance in self.config.data.instances:
            self.organize(instance)

    def organize(self, instance: Instance) -> None:
        
        print("organizing instance", str(instance))
        
        for (type, target) in self.target.items():
            
            if not instance.hasType(type):
                print(f"type {str(type)} not in instance. all types are:")
                for d in instance.data:
                    print("> ", str(d.type), d.abspath)
                continue

            # get input file path
            inp_data = instance.getData(type)

            # create target directory if required
            if not os.path.isdir(target):
                os.makedirs(target)

            # define out file (use random names to qurantee uniqueness and keep reference)
            # TODO: allow user sspecific patterns
            # FUTURE: we could parse (some) dicom headers on a Instance level and use them to create (unique?!) file names.
            rnd = str(uuid.uuid4())
            

            # TODO: then we have to deal with the file extensions.
            # this should be handled by the datatype, especially the edgecases (i.e., nifti having the compressed .nii.gz and uncompressed type .nii, or for dicom beeing a folder) 
            ext = {
                FileType.DICOM:     "",
                FileType.NIFTI:     ".nii.gz",
                FileType.NRRD:      ".nrrd",
                FileType.DICOMSEG:  ".seg",
                FileType.RTSTRUCT:  ".dcm"
            }[type.ftype]
            
            out_file = rnd + ext

            # add to instance
            # TODO: the data is now outside of our managed file structure but should still be linked to the instance. For now, just set the base path. However, this will cause type duplications thus not yet compatible with conversion modules applied afterwards. However, we've to decide if we enforce all conversion steps to only operate on our internal data structure.
            out_data = InstanceData(out_file, type)
            out_data.base = target
            instance.addData(out_data)

            # copy
            shutil.copyfile(inp_data.abspath, out_data.abspath)

            
