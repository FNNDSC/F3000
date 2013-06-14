#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import nibabel
import numpy
import tables

# fyborg imports
import _actions
import config
from looper import Looper
from looper_with_matrix import LooperWithMatrix
from utility import Utility

class SurfaceMapping():
  '''
  Mapping of freesurfer surface vertex indices.
  '''

  @staticmethod
  def transform( surface_file, matrix_file, output_surface_file ):
    '''
    '''

    # build the surface transform command
    cmd = config.MRISTRANSFORM_COMMAND
    cmd = cmd.replace( '%surface%', surface_file )
    cmd = cmd.replace( '%matrix%', matrix_file )
    cmd = cmd.replace( '%output_surface%', output_surface_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()


  @staticmethod
  def map( fibers_file, brain_file, lh_smoothwm_file, rh_smoothwm_file, output_fibers_file, scalar_name='smoothwm' ):
    '''
    '''

    actions = [_actions.FySurfaceMapAction( scalar_name, brain_file, lh_smoothwm_file, rh_smoothwm_file )]

    # start the mapping using the looper
    Looper.loop( fibers_file, output_fibers_file, actions )


  @staticmethod
  def super_map( input_file, brain_file, lh_smoothwm_file, rh_smoothwm_file, neighbors, connectivity_matrix_file ):
    '''
    '''
    actions = [_actions.FySuperSurfaceMapAction( 'super', brain_file, lh_smoothwm_file, rh_smoothwm_file, connectivity_matrix_file, neighbors )]
    
    # start the mapping using the looper
    Looper.loop( input_file, os.devnull, actions, True )
    
    # clean-up
    actions[0].close_file()
    


  @staticmethod
  def decimate( surface_file, decimation_level, output_surface_file ):
    '''
    '''

    if float( decimation_level ) >= 1.0:
      # no decimation required
      return

    # build the surface decimation command
    cmd = config.MRISDECIMATE_COMMAND
    cmd = cmd.replace( '%surface%', surface_file )
    cmd = cmd.replace( '%decimation_level%', str( decimation_level ) )
    cmd = cmd.replace( '%output_surface%', output_surface_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()


  @staticmethod
  def inflate( surface_file, output_surface_file ):
    '''
    '''

    # build the surface inflation command
    cmd = config.MRISINFLATE_COMMAND
    cmd = cmd.replace( '%surface%', surface_file )
    cmd = cmd.replace( '%output_surface%', output_surface_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()




