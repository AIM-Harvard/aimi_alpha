"""
    ----------------------------------------
    AIMI TotalSegmentator - processing utils
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    ----------------------------------------
    
"""

import os
import time
import subprocess

def process_patient(pat_id,
                    model_input_folder ,
                    model_output_folder,
                    use_fast_mode = False):
  
  """
  Infer the cardiac substructures using the platipy hybrid model.
  Arguments:
    pat_id              : required - selected patient ID.
    model_input_folder  : required - path to the folder where the data to be inferred should be stored.
    model_output_folder : required - path to the folder where the inferred segmentation masks will be stored.
    use_fast_mode       : optional - whether to use TotalSegmentator in fast mode or not.
  Outputs:
    This function [...]
  """
  
  start_time = time.time()
  
  img_to_process_list = [f for f in os.listdir(model_input_folder) if pat_id in f and (".nii.gz" in f or ".nrrd" in f)]

  assert(len(img_to_process_list) == 1)

  path_to_img = os.path.join(model_input_folder, img_to_process_list[0])
  

  output_lung_fn = pat_id + "_lungseg.nii.gz"
  output_lobes_fn = pat_id + "_lobeseg.nii.gz"
  
  output_lung_path = os.path.join(model_output_folder, output_lung_fn)
  output_lobes_path = os.path.join(model_output_folder, output_lobes_fn)
  
  # run the lung segmentation model (R231)
  bash_command = list()
  bash_command += ["lungmask"]
  bash_command += ["%s"%path_to_img]
  bash_command += ["%s"%output_lung_path]
  bash_command += ["--modelname", "R231"]
  
  bash_return = subprocess.run(bash_command, check = True, text = True)


  # run the lobes segmentation model (LTRCLobes w/R231 fusion)
  bash_command = list()
  bash_command += ["lungmask"]
  bash_command += ["%s"%path_to_img]
  bash_command += ["%s"%output_lobes_path]
  bash_command += ["--modelname", "LTRCLobes_R231"]
  
  bash_return = subprocess.run(bash_command, check = True, text = True)

  elapsed = time.time() - start_time

  print("Done in %g seconds."%elapsed)
  
  