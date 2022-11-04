from typing import Optional

import os
import pyplastimatch as pypla

from Config import Module, Instance, InstanceData, DataType

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
        instances = self.config.data.getInstances(True, DataType.DICOM)
        assert len(instances) > 0

        # execute convert for each instance
        # TODO: add parallelization
        for instance in instances:
            converted = self.convert(instance)

            if converted is not None:
                instance.addData(converted)

# TODO: outsource
class NiftiConverter(DataConverter):
    """
    Conversion module. 
    Convert instance data from dicom to nifti.
    """
    
    def convert(self, instance: Instance) -> None:#-> Optional[InstanceData]:

        # cretae a converted instance
        assert instance.hasType(DataType.DICOM), f"CONVERT ERROR: required datatype (dicom) not available in instance {str(instance)}."
        dicom_data = instance.getDataByType(DataType.DICOM)

        # out data
        nifti_data = InstanceData("image.nii.gz", DataType.NIFTI)
        instance.addData(nifti_data)

        # paths
        inp_dicom_dir = dicom_data.abspath
        out_nifti_file = nifti_data.abspath
        out_log_file = os.path.join(instance.abspath, "_pypla.log")

        # sanity check
        assert(os.path.isdir(inp_dicom_dir))

        # DICOM CT to NRRD conversion (if the file doesn't exist yet)
        if os.path.isfile(out_nifti_file):
            print("CONVERT ERROR: File already exists: ", out_nifti_file)
            #return None
        else:
            convert_args_ct = {
                "input" : inp_dicom_dir,
                "output-img" : out_nifti_file
            }

            # clean old log file if it exist
            if os.path.isfile(out_log_file): 
                os.remove(out_log_file)
            
            # run conversion using plastimatch
            pypla.convert(
                verbose=self.verbose,
                path_to_log_file=out_log_file,
                **convert_args_ct
            )

        #return nifti_data
    