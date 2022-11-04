"""
    ----------------------------------------
    AIMI alpha - run the TS pipeline locally
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    ----------------------------------------
    
"""

import sys
sys.path.append('.')

import os
import shutil

from aimi import general_utils as aimi_utils
from aimi import totalsegmentator as aimi_model

# FIXME: parse everything from config file
dataset_name = "dataset"

path_to_dicomsort_repo = "/app/"

data_base_path = "/app/data/"
raw_base_path = os.path.join(data_base_path, "input_data")
sorted_base_path = os.path.join(data_base_path, "sorted")

processed_base_path = os.path.join(data_base_path, "processed")
processed_nifti_path = os.path.join(processed_base_path, "nii")
processed_dicomseg_path = os.path.join(processed_base_path, "dicomseg")

model_input_folder = os.path.join(data_base_path, "model_input")
model_output_folder = os.path.join(data_base_path, "totalsegmentator_output/")

dicomseg_json_path = "/app/aimi/totalsegmentator/config/dicomseg_metadata_whole.json"

docker_base_out_path = os.path.join(data_base_path, "output_data")
docker_out_path = os.path.join(docker_base_out_path, "totalsegmentator")

# FIXME: create directory tree using a function?
# N.B. - some of these (mounting points) need to be created
# at build time for the user to properly access them

dir_to_create = [sorted_base_path, processed_base_path,
                 processed_nifti_path, processed_dicomseg_path,
                 model_input_folder, model_output_folder]

assert(os.path.exists(raw_base_path) and os.path.isfile(dicomseg_json_path))

for d in dir_to_create:
  if not os.path.exists(d):
    os.makedirs(name = d, mode = 0o777)

# input data sorting and prepping
aimi_utils.sort_patient_data(raw_base_path = raw_base_path,
                             sorted_base_path = sorted_base_path,
                             path_to_dicomsort_repo = path_to_dicomsort_repo)

# FIXME: this needs to be handled properly later
# Either we loop on all of the subjects, or we at least implement some control
assert(len(os.listdir(sorted_base_path)) == 1)
pat_id = os.listdir(sorted_base_path)[0]

# FIXME: do we want to check which patients have a segmask already and skip those?

# DICOM CT to NIfTI - required for the processing
aimi_utils.preprocessing.pypla_dicom_ct_to_nifti(sorted_base_path = sorted_base_path,
                                                 processed_nifti_path = processed_nifti_path,
                                                 pat_id = pat_id, verbose = True)

# prepare the `model_input` folder for the inference phase
aimi_utils.preprocessing.prep_ct_input_data(processed_nifti_path = processed_nifti_path,
                                            model_input_folder = model_input_folder,
                                            pat_id = pat_id)

aimi_model.utils.processing.process_patient(pat_id = pat_id,
                                            model_input_folder = model_input_folder,
                                            model_output_folder = model_output_folder)

processed_seg_folder = os.path.join(processed_nifti_path, pat_id, "totalsegmentator")
shutil.copytree(model_output_folder, processed_seg_folder)

# convert to DICOMSEG
aimi_model.utils.postprocessing.nifti_to_dicomseg(sorted_base_path = sorted_base_path,
                                                  processed_base_path = processed_base_path,
                                                  dicomseg_json_path = dicomseg_json_path,
                                                  pat_id = pat_id)

# FIXME: add the possibility to export more data than a simple DICOMSEG file from config file?
shutil.copytree(processed_base_path, docker_out_path, dirs_exist_ok = True)