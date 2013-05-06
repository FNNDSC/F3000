#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import dipy.align.aniso2iso as resampler
import nibabel

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
  def register( input_file, target_file, output_directory ):
    '''
    Register the input image to match the target image using ANTs.
    
    input
      the input file path
    target
      the target file path
    output_directory
      the output directory
      
    The final output file is deformed.nii.gz in the output directory.
    '''

    #output_prefix = os.path.join( output_directory, os.path.splitext( os.path.basename( input_file ) )[0] )
    output_prefix = os.path.normpath(output_directory) + os.sep

    # configure the ANTs environment
    cmd = 'export ANTSPATH=' + config.ANTS_BIN_DIR + ';'
    # change to ouput directory
    cmd += 'cd ' + output_directory + ';'
    # run ants.sh
    cmd += '$ANTSPATH/ants.sh 3 ' + target_file + ' ' + input_file + ' ' + output_prefix
    sp = subprocess.Popen( ["/bin/bash", "-i", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()
