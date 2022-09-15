"""
    ----------------------------------------
    AIME nnU-Net Pancreas - post-processing utils
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

def preprocessing():
  
  print("a")