"""
    ----------------------------------------
    AIMI nnU-Net Abdominal OAR - post-processing utils
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

import numpy as np
import SimpleITK as sitk
import pyplastimatch as pypla

def pypla_nifti_to_nrrd(pred_nifti_path, processed_nrrd_path,
                        pat_id, verbose = True):
  
  """
  NIfTI to NRRD file conversion using PyPlastimatch. 
  Arguments:
    src_folder : required - path to the folder where the sorted data should be stored.
    dst_folder : required - path to the folder where the preprocessed NRRD data are stored
    pat_id     : required - patient ID (used for naming purposes).
  
  Returns:
    pred_nrrd_path - 
  Outputs:
    This function [...]
  """

  pred_nrrd_path = os.path.join(processed_nrrd_path, pat_id, pat_id + "_pred_abdominal_oar.nrrd")
  log_file_path = os.path.join(processed_nrrd_path, pat_id, pat_id + "_pypla.log")
  
  # Inferred NIfTI segmask to NRRD
  convert_args_pred = {"input" : pred_nifti_path, 
                       "output-img" : pred_nrrd_path}

  pypla.convert(verbose = verbose,
                path_to_log_file = log_file_path,
                **convert_args_pred)
  
  return pred_nrrd_path

# ----------------------------------
# ----------------------------------

def pypla_postprocess(processed_nrrd_path, model_output_folder, pat_id):

  """
  Wrapper for NIfTI to NRRD file conversion using PyPlastimatch.
  Arguments:
    processed_nrrd_path  : required - path to the folder where the sorted data should be stored.
    model_output_folder  : required - path to the folder where the inferred segmentation masks should be stored.
    pat_id               : required - patient ID (used for naming purposes). 
  Outputs:
    This function [...]
  """

  pred_nifti_fn = pat_id + ".nii.gz"
  pred_nifti_path = os.path.join(model_output_folder, pred_nifti_fn)

  pred_nrrd_path = pypla_nifti_to_nrrd(pred_nifti_path = pred_nifti_path,
                                       processed_nrrd_path = processed_nrrd_path,
                                       pat_id = pat_id, verbose = True)

# ----------------------------------
# ----------------------------------

def numpy_to_nrrd(model_output_folder, processed_nrrd_path, pat_id,
                  output_folder_name = "pred_softmax", output_dtype = "uint8",
                  structure_list = ["Background", "Spleen",
                                    "Kidney_R", "Kidney_L",
                                    "Gallbladder", "Esophagus",
                                    "Liver", "Stomach",
                                    "Aorta", "Inferior_vena_cava",
                                    "Portal_and_splenic_vein", "Pancreas",
                                    "Adrenal_gland_R", "Adrenal_gland_L"]):

  """
  Convert softmax probability maps to NRRD. For simplicity, the probability maps
  are converted by default to UInt8
  Arguments:
    model_output_folder : required - path to the folder where the inferred segmentation masks should be stored.
    processed_nrrd_path : required - path to the folder where the preprocessed NRRD data are stored.
    pat_id              : required - patient ID (used for naming purposes).
    output_folder_name  : optional - name of the subfolder under the patient directory 
                                     (under `processed_nrrd_path`) where the softmax NRRD
                                     files will be saved. Defaults to "pred_softmax".
    output_dtype        : optional - output data type. Data type float16 is not supported by the NRRD standard,
                                     so the choice should be between uint8, uint16 or float32. Please note this
                                     will greatly impact the size of the DICOM PM file that will be generated.
    structure_list      : optional - list of the structures whose probability maps are stored in the 
                                     first channel of the `.npz` file (output from the nnU-Net pipeline
                                     when `export_prob_maps` is set to True). Defaults to the structure
                                     list for the Abdominal OAR model (background = 0 included).
  Outputs:
    This function [...]
  """

  pred_softmax_fn = pat_id + ".npz"
  pred_softmax_path = os.path.join(model_output_folder, pred_softmax_fn)

  # parse NRRD file - we will make use of if to populate the header of the
  # NRRD mask we are going to get from the inferred segmentation mask
  ct_nrrd_path = os.path.join(processed_nrrd_path, pat_id, pat_id + "_CT.nrrd")
  sitk_ct = sitk.ReadImage(ct_nrrd_path)

  output_folder_path = os.path.join(processed_nrrd_path, pat_id, output_folder_name)
  
  if not os.path.exists(output_folder_path):
    os.mkdir(output_folder_path)

  pred_softmax_all = np.load(pred_softmax_path)["softmax"]

  # check if the model managed to segment the pancreatic cancer as well
  # if not, exclude it from the list
  has_cancer_seg = True if len(np.unique(pred_softmax_all)) > 2 else False

  if has_cancer_seg == False:
    structure_list = ["Background", "Pancreas"]

  for channel, structure in enumerate(structure_list):

    pred_softmax_segmask = pred_softmax_all[channel].astype(dtype = np.float32)

    assert(output_dtype in ["uint8", "uint16", "float32"])      

    if output_dtype == "float32":
      # no rescale needed - the values will be between 0 and 1
      # set SITK image dtype to Float32
      sitk_dtype = sitk.sitkFloat32

    elif output_dtype == "uint8":
      # rescale between 0 and 255, quantize
      pred_softmax_segmask = (255*pred_softmax_segmask).astype(np.int32)
      # set SITK image dtype to UInt8
      sitk_dtype = sitk.sitkUInt8

    elif output_dtype == "uint16":
      # rescale between 0 and 65536
      pred_softmax_segmask = (65536*pred_softmax_segmask).astype(np.int32)
      # set SITK image dtype to UInt16
      sitk_dtype = sitk.sitkUInt16
    
    pred_softmax_segmask_sitk = sitk.GetImageFromArray(pred_softmax_segmask)
    pred_softmax_segmask_sitk.CopyInformation(sitk_ct)
    pred_softmax_segmask_sitk = sitk.Cast(pred_softmax_segmask_sitk, sitk_dtype)

    output_fn = "%s.nrrd"%(structure)
    output_path = os.path.join(output_folder_path, output_fn)

    writer = sitk.ImageFileWriter()

    writer.UseCompressionOn()
    writer.SetFileName(output_path)
    writer.Execute(pred_softmax_segmask_sitk)
    
# ----------------------------------
# ----------------------------------      
    
# TO-DO
def numpy_to_nifti(model_output_folder, processed_nrrd_path, pat_id,
                   output_folder_name = "pred_softmax", output_dtype = "uint8",
                   structure_list = ["Background", "Spleen",
                                     "Kidney_R", "Kidney_L",
                                     "Gallbladder", "Esophagus",
                                     "Liver", "Stomach",
                                     "Aorta", "Inferior_vena_cava",
                                     "Portal_and_splenic_vein", "Pancreas",
                                     "Adrenal_gland_R", "Adrenal_gland_L"]):
  
  """
  Convert softmax probability maps to NIfTI. For simplicity, the probability maps
  are converted by default to UInt8
  Arguments:
    model_output_folder  : required - path to the folder where the inferred segmentation masks should be stored.
    processed_nifti_path : required - path to the folder where the preprocessed NRRD data are stored.
    pat_id               : required - patient ID (used for naming purposes).
    output_folder_name   : optional - name of the subfolder under the patient directory 
                                      (under `processed_nrrd_path`) where the softmax NRRD
                                      files will be saved. Defaults to "pred_softmax".
    output_dtype         : optional - output data type. Data type float16 is not supported by the NRRD standard,
                                      so the choice should be between uint8, uint16 or float32. Please note this
                                      will greatly impact the size of the DICOM PM file that will be generated.
    structure_list       : optional - list of the structures whose probability maps are stored in the 
                                      first channel of the `.npz` file (output from the nnU-Net pipeline
                                      when `export_prob_maps` is set to True). Defaults to the structure
                                      list for the Abdominal OAR model (background = 0 included).
  Outputs:
    This function [...]
  """
  
  print("Convert softmax probability maps to NIfTI.")
  
  print("\nStill to be implemented.")  
  
# ----------------------------------
# ----------------------------------      
    
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
  pat_dir_dicomseg_path = os.path.join(processed_dicomseg_path, pat_id)

  if not os.path.exists(pat_dir_dicomseg_path):
    os.mkdir(pat_dir_dicomseg_path)

  pred_segmasks_nifti = os.path.join(processed_nifti_path, pat_id, pat_id + "_pred_abdominal_oar.nii.gz")

  dicom_seg_out_path = os.path.join(pat_dir_dicomseg_path, pat_id + "_SEG.dcm")

  bash_command = list()
  bash_command += ["itkimage2segimage"]
  bash_command += ["--inputImageList", "%s"%pred_segmasks_nifti]
  bash_command += ["--inputDICOMDirectory", "%s"%path_to_ct_dir]
  bash_command += ["--outputDICOM", "%s"%dicom_seg_out_path]
  bash_command += ["--inputMetadata", "%s"%dicomseg_json_path]

  if skip_empty_slices == True:
    bash_command += ["--skip"]

  bash_return = subprocess.run(bash_command, check = True, text = True)
