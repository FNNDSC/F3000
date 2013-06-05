#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyCherrypickFreesurfer():
  '''
  Grab and convert relevant files from a FREESURFER SUBJECT directory.
  '''

  @staticmethod
  def run( input, output, tempdir ):
    '''
    Runs the mapping stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input freesurfer directory!' )

    if not os.path.exists( output ):
      # create output directory
      os.mkdir( output )

    # use a temporary workspace
    # .. and copy all working files
    brain_file = os.path.join( tempdir, 'brain.nii.gz' )
    output_brain_file = os.path.join( output, os.path.basename( brain_file ) )
    segmentation_file = os.path.join( tempdir, 'aparc+aseg.nii.gz' )
    output_segmentation_file = os.path.join( output, os.path.basename( segmentation_file ) )
    lh_smoothwm_file = os.path.join( tempdir, 'lh.smoothwm' )
    output_lh_smoothwm_file = os.path.join( output, os.path.basename( lh_smoothwm_file ) )
    rh_smoothwm_file = os.path.join( tempdir, 'rh.smoothwm' )
    output_rh_smoothwm_file = os.path.join( output, os.path.basename( rh_smoothwm_file ) )

    # 1. STEP: cherrypick
    Utility.parseFreesurferDir( input, brain_file, segmentation_file, lh_smoothwm_file, rh_smoothwm_file )

    # 2. STEP: copy data to the proper output places
    shutil.copy( brain_file, output )
    shutil.copy( segmentation_file, output )
    shutil.copy( lh_smoothwm_file, output )
    shutil.copy( rh_smoothwm_file, output )

    return output_brain_file, output_segmentation_file, output_lh_smoothwm_file, output_rh_smoothwm_file


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Grab and convert relevant files from a FREESURFER SUBJECT directory.' )

  entrypoint.add_input( 'i', 'input', 'The input FREESURFER directory.' )
  entrypoint.add_input( 'o', 'output', 'The output directory.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running'

  if not options.verbose:
    sys.stdout = open(os.devnull,'wb')

  a, b, c, d = FyCherrypickFreesurfer.run( options.input, options.output, tempdir )

  sys.stdout = sys.__stdout__

  print 'Done!'
  print 'Output brain file: ', a
  print 'Output segmentation file: ', b
  print 'Output lh_smoothwm file: ', c
  print 'Output rh_smoothwm file: ', d
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
