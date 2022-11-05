from typing import Optional

from Config import Instance, InstanceData, DataType, FileType, Meta, SEG
from .DataConverter import DataConverter

import subprocess

# TODO: we should have a generator for instance data (e.g., on the Instance class)

# TODO: Dicomseg generation so far epends on the model. This should, however, be more independend. Ideally, a segmentation carries information about it's ROI in the DataType metatada (will be targeted in the upcoming DataType revision). This can be used to the generate the conversion file dynamicaly and model independend (of course each model has to populate a maping of it's segmentations but that's A simpler, B functional for other use cases too)

class DsegConverter(DataConverter):
    def convert(self, instance: Instance) -> Optional[InstanceData]:
        
        # converter config
        # TODO: load from gobal config>model section
        c = {
            "skip_empty_slices": True
        }

        # test
        if self.verbose: instance.printDataMetaOverview(label="Instance Data")
        fdata = instance.filterData(DataType(FileType.NIFTI, SEG))
        if self.verbose: instance.printDataMetaOverview(datas=fdata, label="After Filtering")

        # get segmentation paths list
        pred_segmasks_nifti_list = [d.abspath for d in fdata]
        
        # TODO: old approach, only valid as long all segmentations are in the same folder.
        pred_segmasks_nifti_list = ",".join(sorted(pred_segmasks_nifti_list))

        # get dicom data
        dicom_data = instance.getData(DataType(FileType.DICOM))

        # output data
        out_data = InstanceData("seg.dcm", DataType(FileType.DICOMSEG))
        #instance.addData(out_data)
        out_data.instance = instance

        # build command
        bash_command  = ["itkimage2segimage"]
        bash_command += ["--inputImageList", pred_segmasks_nifti_list]
        bash_command += ["--inputDICOMDirectory", dicom_data.abspath]
        bash_command += ["--outputDICOM", out_data.abspath]
        bash_command += ["--inputMetadata", self.config.dicomseg_json_path]

        if c["skip_empty_slices"] == True:
            bash_command += ["--skip"]

        print("bash_command", bash_command)

        # execute command
        bash_return = subprocess.run(bash_command, check = True, text = True)
            
        #TODO: check success, return either None or InstanceData
        return out_data