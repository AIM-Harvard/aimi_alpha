"""
    ----------------------------------------
    AIMI alpha - local utils
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    ----------------------------------------
    
"""

import os
import time
import shutil
import subprocess


def sort_patient_data(raw_base_path, sorted_base_path, path_to_dicomsort_repo,
                      sorted_structure = "%%SeriesInstanceUID/%%SOPInstanceUID.dcm"):

  """
  Download raw DICOM data and run dicomsort to standardise the input format.
  Arguments:
    raw_base_path    : required - path to the folder where the raw data is stored.
                                  This folder should be mounted as a volume in Docker, and must be
                                  exposed to both the container and the local node
    sorted_base_path : required - path to the folder where the sorted data will be stored.
                                  This folder should be internal and not exposed to the local node (disposable)
    remove_raw       : optional - whether to remove or not the raw non-sorted data
                                  (after sorting with dicomsort). Defaults to True.
    sorted_structure : optional - structure of the sorted directory.
                                  Defaults to $sorted_base_path/$SeriesInstanceUID/$SOPInstanceUID.dcm
    
    # FIXME - get rid of this once DICOMsort gets released as a package (... soon)!
    path_to_dicomsort_repo : optional - path to the folder where the dicomsort
                                        repository is found/cloned from GitHub
  Outputs:
    This function [...]
  """

  start_time = time.time()
  print("\nSorting DICOM files..." )

  dicomsort_py_path = os.path.join(path_to_dicomsort_repo, "dicomsort/dicomsort.py")
  bash_command = list()
  bash_command += ["python", "%s"%dicomsort_py_path, "-k", "-u",
                   "%s"%raw_base_path, "%s/%s"%(sorted_base_path, sorted_structure)]

  bash_return = subprocess.run(bash_command, check = True, text = True)

  elapsed = time.time() - start_time
  print("Done in %g seconds."%elapsed)

  print("Sorted DICOM data saved at: %s"%(os.path.join(sorted_base_path)))