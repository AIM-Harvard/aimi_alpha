"""
    ----------------------------------------
    AIMI PlatiPy - processing utils
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
                    path_to_config_file = None):
  
  """
  Infer the cardiac substructures using the platipy hybrid model.
  Arguments:
    pat_id              : required - selected patient ID.
    model_input_folder  : required - path to the folder where the data to be inferred should be stored.
    model_output_folder : required - path to the folder where the inferred segmentation masks will be stored.
    path_to_config_file : optional - path to a custom configuration file for the Platipy pipeline.
  Outputs:
    This function [...]
  """
  
  start_time = time.time()
  
  img_to_process_list = [f for f in os.listdir(model_input_folder) if pat_id in f and (".nii.gz" in f or ".nrrd" in f)]

  assert(len(img_to_process_list) == 1)

  path_to_img = os.path.join(model_input_folder, img_to_process_list[0])

  bash_command = list()
  bash_command += ["platipy", "segmentation", "cardiac"]
  bash_command += ["-o", "%s"%model_output_folder]
  bash_command += ["%s"%path_to_img]

  if path_to_config_file is not None:
    print("Running the hybrid cardiac segmentation with config file at: %s"%(path_to_config_file))
    bash_command += ["--config", "%s"%path_to_config_file]
  else:
    print("Running the hybrid cardiac segmentation with default configuration.")

  bash_return = subprocess.run(bash_command, check = True, text = True)

  elapsed = time.time() - start_time

  print("Done in %g seconds."%elapsed)
  
  