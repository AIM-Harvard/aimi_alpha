from Config import Instance, InstanceData, DataType, FileType
from .DataConverter import DataConverter

import os, subprocess

# TODO: we should have a generator for instance data (e.g., on the Instance class)

# TODO: Dicomseg generation so far epends on the model. This should, however, be more independend. Ideally, a segmentation carries information about it's ROI in the DataType metatada (will be targeted in the upcoming DataType revision). This can be used to the generate the conversion file dynamicaly and model independend (of course each model has to populate a maping of it's segmentations but that's A simpler, B functional for other use cases too)

class DsegConverter(DataConverter):
    def convert(self, instance: Instance) -> None:
        
        # converter config
        # TODO: load from gobal config>model section
        c = {
            "skip_empty_slices": True
        }

        # get all segmentations that we want to include
        pred_segmasks_nifti_list = []
        for data in instance.data:

            # ignore all datatypes except the supported ones
            if data.type.ftype != FileType.NIFTI:
                continue

            # filter based on usecase
            # TODO: this will be corrected during the DataType revision

            if data.type.getMeta("modality") != "seg":
                continue

            #
            pred_segmasks_nifti_list.append(data.abspath)
        
        # TODO: old approach, only valid as long all segmentations are in the same folder.
        pred_segmasks_nifti_list = ",".join(sorted(pred_segmasks_nifti_list))

        # get dicom data
        dicom_data = instance.getDataByType(DataType(FileType.DICOM))

        # output data
        out_data = InstanceData("seg.dcm", DataType(FileType.DICOMSEG))
        instance.addData(out_data)

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
            