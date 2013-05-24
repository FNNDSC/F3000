#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import nibabel
import numpy

# fyborg imports
import _actions
import config
from looper import Looper
from utility import Utility

class Mapping():
  '''
  Mapping of scalar volumes.
  '''

  @staticmethod
  def map(fibers_file, volume_files, output_fibers_file):
    '''
    '''
    actions = []
  
    for v in volume_files:
      volume_name = os.path.splitext(os.path.basename(v))[0]
      # if extension was .nii.gz, also get rid of .nii
      volume_name = volume_name.replace('.nii','')
      
      actions.append(_actions.FyMapAction(volume_name, v))
    
    # start the mapping using the looper
    Looper.loop(fibers_file, output_fibers_file, actions)
    
  