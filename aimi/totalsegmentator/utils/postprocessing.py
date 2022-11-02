"""
    ----------------------------------------
    AIMI TotalSegmentator - post-processing utils
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    ----------------------------------------
    
"""

import os
import shutil
import subprocess

import json


def nifti_to_dicomseg(sorted_base_path, processed_base_path,
                      dicomseg_json_path, pat_id, skip_empty_slices = True):

  """
  Export DICOM SEG object from segmentation masks stored in NRRD files.
  Arguments:
    sorted_base_path    : required - path to the folder where the sorted data should be stored.
    processed_base_path : required - path to the folder where the preprocessed NIfTI data are stored
    dicomseg_json_path  : required - JSON storing the metadata information to convert the segmentation
                                     volume into DICOM SEG format.
    pat_id              : required - patient ID (used for naming purposes). 
    skip_empty_slices   : optional - skip encoding of empty slices in the DICOMSEG object.
                                     If true, allows for (at least) slight file size reduction.
  Outputs:
    This function [...]
  """

  path_to_ct_dir = os.path.join(sorted_base_path, pat_id, "CT")

  processed_nifti_path = os.path.join(processed_base_path, "nii")
  processed_dicomseg_path = os.path.join(processed_base_path, "dicomseg")
  
  pat_dir_nifti_path = os.path.join(processed_nifti_path, pat_id)
  pat_dir_dicomseg_path = os.path.join(processed_dicomseg_path, pat_id)

  if not os.path.exists(pat_dir_dicomseg_path):
    os.mkdir(pat_dir_dicomseg_path)

  totalsegmentator_output_folder = os.path.join(pat_dir_nifti_path, "seg")

  pred_struct_list = [struct for struct in sorted(os.listdir(totalsegmentator_output_folder))]

  pred_segmasks_nifti_list = [os.path.join(totalsegmentator_output_folder, struct) for struct in pred_struct_list]
  pred_segmasks_nifti_list = ",".join(pred_segmasks_nifti_list)

  dicom_seg_out_path = os.path.join(pat_dir_dicomseg_path, pat_id + "_SEG.dcm")

  bash_command = list()
  bash_command += ["itkimage2segimage"]
  bash_command += ["--inputImageList", "%s"%pred_segmasks_nifti_list]
  bash_command += ["--inputDICOMDirectory", "%s"%path_to_ct_dir]
  bash_command += ["--outputDICOM", "%s"%dicom_seg_out_path]
  bash_command += ["--inputMetadata", "%s"%dicomseg_json_path]

  if skip_empty_slices == True:
    bash_command += ["--skip"]

  bash_return = subprocess.run(bash_command, check = True, text = True)
    