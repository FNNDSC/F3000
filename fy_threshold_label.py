#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# third-party imports
import nibabel

# fyborg imports
from _core import *


class FyThresholdLabel():
  '''
  Threshold a TrackVis file using a Freesurfer label file.
  '''

  @staticmethod
  def run( input, label, scalarname, hemisphere, left_hemi, right_hemi, output, tempdir ):
    '''
    Runs the mapping stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input fibers file!' )

    if not os.path.exists( label ):
      raise Exception( 'Could not find the input labels file!' )

    if not os.path.exists( left_hemi ):
      raise Exception( 'Could not find the input left hemisphere surface file!' )

    if not os.path.exists( right_hemi ):
      raise Exception( 'Could not find the input right hemisphere surface file!' )

    # check mode
    if hemisphere == 'auto':
      # try to auto-detect
      if os.path.basename( label ).startswith( 'lh.' ):
        hemisphere = 'left'
      elif os.path.basename( label ).startswith( 'rh.' ):
        hemisphere = 'right'
      else:
        raise Exception( 'Auto-detection of hemisphere failed!' )

    # calculate offset
    if hemisphere == 'right':
      offset = len( nibabel.freesurfer.read_geometry( left_hemi )[0] )
    else:
      offset = 0

    # use a temporary workspace
    # .. and copy all working files
    input_file = os.path.join( tempdir, os.path.basename( input ) )
    label_file = os.path.join( tempdir, os.path.basename( label ) )

    left_hemi_file = os.path.join( tempdir, os.path.basename( left_hemi ) )
    right_hemi_file = os.path.join( tempdir, os.path.basename( right_hemi ) )

    output_file = os.path.join( tempdir, os.path.basename( output ) )

    shutil.copy( input, input_file )
    shutil.copy( label, label_file )
    shutil.copy( left_hemi, left_hemi_file )
    shutil.copy( right_hemi, right_hemi_file )

    # 1. STEP: threshold the input fibers
    Thresholding.threshold_by_label( input_file, scalarname, label_file, offset, output_file )

    # 2. STEP: copy data to the proper output places
    shutil.copyfile( output_file, output )

    return hemisphere, output

#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Threshold a TrackVis file using a Freesurfer label file. This requires mapped vertices.' )

  entrypoint.add_input( 'i', 'input', 'The input TrackVis file.' )
  entrypoint.add_input( 'l', 'label', 'The input Freesurfer label file.' )
  entrypoint.add_input( 'n', 'scalarname', 'The scalar name of mapped vertices.' )
  entrypoint.add_choices( 'hemisphere', ['left', 'right', 'auto'], 'The corresponding hemisphere of the label file. LEFT, RIGHT or AUTO for auto-detection. DEFAULT: auto', 'auto' )
  entrypoint.add_input( 'lh', 'left_hemi', 'The left hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'rh', 'right_hemi', 'The right hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'o', 'output', 'The output TrackVis file.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )

  a, b = FyThresholdLabel.run( options.input, options.label, options.scalarname, options.hemisphere, options.left_hemi, options.right_hemi, options.output, tempdir )

  sys.stdout = sys.__stdout__

  print 'Hemisphere: ', a
  print 'Output filtered TrackVis file: ', b
  print 'Done!'
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
