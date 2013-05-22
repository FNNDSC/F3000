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
  def invert_matrix( matrix_file, inverse_matrix_file ):
    '''
    Load a FLIRT matrix file and store an inverted version.
    
    matrix_file
      the original matrix file path
    inverse_matrix_file
      the inverted matrix output file path
    '''

    # load the matrix
    matrix = numpy.matrix( numpy.loadtxt( matrix_file ) )

    # store the inverse matrix
    numpy.savetxt( inverse_matrix_file, matrix.I, fmt='%10.13f', delimiter='  ' )


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
  def register( diffusion_file, brain_file, matrix_file, warped_diffusion_file, arguments='' ):
    '''
    Register the diffusion image to match the target brain image using the config.REGISTRATION_COMMAND.
    
    diffusion_file
      the input diffusion file path
    brain_file
      the target brain file path
    matrix_file
      the output registration matrix
    warped_diffusion_file
      the warped diffusion output file path      
    arguments
      any additional arguments
    '''

    # build the registration command
    cmd = config.REGISTRATION_COMMAND
    cmd = cmd.replace( '%diffusion%', diffusion_file )
    cmd = cmd.replace( '%brain%', brain_file )
    cmd = cmd.replace( '%matrix%', matrix_file )
    cmd = cmd.replace( '%warped_diffusion%', warped_diffusion_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()


  @staticmethod
  def warp( segmentation_file, diffusion_file, inverse_matrix_file, warped_segmentation_file ):
    '''
    Warp a label map to diffusion space using the provided matrix.
    
    segmentation_file
      the input segmentation file path
    diffusion_file
      the diffusion reference image
    inverse_matrix_file
      the .mat file to use as a transform
    warped_segmentation_file
      the warped output image
    '''

    # build the warp command
    cmd = config.TRANSFORM_COMMAND
    cmd = cmd.replace( '%segmentation%', segmentation_file )
    cmd = cmd.replace( '%diffusion%', diffusion_file )
    cmd = cmd.replace( '%inverse_matrix%', inverse_matrix_file )
    cmd = cmd.replace( '%warped_segmentation%', warped_segmentation_file )
    print cmd
    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()


  @staticmethod
  def warp_fibers( fibers_file, diffusion_file, brain_file, matrix_file, warped_fibers_file, arguments='' ):
    '''
    Warp (transform) fibers using the config.TRACK_TRANSFORM_COMMAND.
    
    fibers_file
      the file to warp
    diffusion_file
      the original diffusion volume
    brain_file
      the original structural scan (target space)
    matrix_file
      the FLIRT registration matrix
    warped_fibers_file
      the output file
    arguments
      any additional arguments
    
    '''
    # build the transform command
    cmd = config.TRACK_TRANSFORM_COMMAND
    cmd = cmd.replace( '%fibers%', fibers_file )
    cmd = cmd.replace( '%diffusion%', diffusion_file )
    cmd = cmd.replace( '%brain%', brain_file )
    cmd = cmd.replace( '%matrix%', matrix_file )
    cmd = cmd.replace( '%warped_fibers%', warped_fibers_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()

