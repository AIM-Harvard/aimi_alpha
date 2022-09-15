"""
    ----------------------------------------
    AIME alpha - config utils
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    ----------------------------------------
    
"""

import copy
import json

def modify_dicomseg_json_file(dicomseg_json_path, new_dicomseg_json_path, SegmentAlgorithmName):

  """
  Update the DICOMSEG metadata JSON file setting "SegmentAlgorithmName" to the specific model
  used for segmentation purposes.

  Arguments:
    dicomseg_json_path     : path to the original DICOMSEG JSON file 
    new_dicomseg_json_path : path to the updated DICOMSEG JSON file
    SegmentAlgorithmName   : name of the segmentation algorithm that will populate
                             the "SegmentAlgorithmName" in the DICOMSEG file

  """
  
  f = open(dicomseg_json_path)
  dicomseg_json = json.load(f)

  new_dicomseg_json = copy.deepcopy(dicomseg_json)
  n_fields = len(new_dicomseg_json['segmentAttributes'])
  
  for n in range(0, n_fields): 
    new_dicomseg_json['segmentAttributes'][n][0]['SegmentAlgorithmName'] = SegmentAlgorithmName

  with open(new_dicomseg_json_path, 'w') as f: 
    json.dump(new_dicomseg_json, f, indent = 2)



