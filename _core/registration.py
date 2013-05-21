#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import dipy.align.aniso2iso as resampler
import nibabel
import numpy

# fyborg imports
import config
from utility import Utility

class Registration():
  '''
  Registration steps and related actions.
  '''

  @staticmethod
  def resample( input_file, target_file, output_file, interpolation=0 ):
    '''
    Resample the input image to match the target image.
    
    input_file
      the input file path
    target_file
      the target file path
    output_file
      the output file path    
    '''
    # load the input image
    input_image = nibabel.load( input_file )

    # load the target image
    target_image = nibabel.load( target_file )

    # configure the zooms
    old_zooms = input_image.get_header().get_zooms()[:3]
    new_zooms = target_image.get_header().get_zooms()[:3]

    # .. and the affine
    affine = input_image.get_affine()
    # .. and header
    header = input_image.get_header()

    # resample the input to match the target
    resampled_data, new_affine = resampler.resample( input_image.get_data(), affine, old_zooms, new_zooms, interpolation )

    # save the resampled image
    klass = input_image.__class__
    nibabel.save( klass( resampled_data, new_affine, header ), output_file )


  @staticmethod
  def register( input_file, target_file, matrix_file ):
    '''
    Register the input image to match the target image using FLIRT.
    
    input_file
      the input file path
    target_file
      the target file path
    matrix_file
      the output registration matrix

    '''

    # build the FLIRT command
    cmd = config.FLIRT_BIN_PATH + ' -in ' + input_file + ' -ref ' + target_file + ' -omat ' + matrix_file + ' ' + FLIRT_ARGUMENTS + ';'

    sp = subprocess.Popen( ["/bin/bash", "-i", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()


  def warp_fibers(fibers_file, diffusion_file, brain_file, matrix_file, output_file):
    '''
    Warp (transform) a TrackVis file using a FLIRT registration matrix.
    
    fibers_file
      the .trk-file to warp
    diffusion_file
      the original diffusion volume
    brain_file
      the original structural scan (target space)
    matrix_file
      the FLIRT registration matrix
    output_file
      the output .trk-file
    
    '''
    
    # build the track_transform command
    cmd = config.TRACK_TRANSFORM_BIN_PATH + ' ' + fibers_file + ' ' + output_file + ' -src ' + diffusion_file + ' -ref ' + brain_file + ' -reg ' + matrix_file + ';'

    sp = subprocess.Popen( ["/bin/bash", "-i", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()
    
