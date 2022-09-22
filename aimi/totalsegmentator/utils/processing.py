"""
    ----------------------------------------
    AIME nnU-Net Pancreas - processing utils
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

  bash_command = list()
  bash_command += ["TotalSegmentator"]
  bash_command += ["-i", "%s"%path_to_img]
  bash_command += ["-o", "%s"%model_output_folder]

  if use_fast_mode:
    print("Running TotalSegmentator in fast mode ('--fast', 3mm): ")
    bash_command += ["--fast"]
  else:
    print("Running TotalSegmentator in default mode (1.5mm)")

  bash_return = subprocess.run(bash_command, check = True, text = True)

  elapsed = time.time() - start_time

  print("Done in %g seconds."%elapsed)
  
  