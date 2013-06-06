#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FySurfaceConnectivity():
  '''
  Create a connectivity matrix of vertices.
  '''

  @staticmethod
  def run( input, left_hemi, right_hemi, scalarname, output, tempdir ):
    '''
    Runs the connectivity matrix stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input fibers file!' )

    if not os.path.exists( left_hemi ):
      raise Exception( 'Could not find the input left hemisphere surface file!' )

    if not os.path.exists( right_hemi ):
      raise Exception( 'Could not find the input right hemisphere surface file!' )

    # use a temporary workspace
    # .. and copy all working files
    input_file = os.path.join( tempdir, os.path.basename( input ) )
    left_hemi_file = os.path.join( tempdir, os.path.basename( left_hemi ) )
    right_hemi_file = os.path.join( tempdir, os.path.basename( right_hemi ) )

    output_file = os.path.join( tempdir, os.path.basename( output ) )

    shutil.copy( input, input_file )
    shutil.copy( left_hemi, left_hemi_file )
    shutil.copy( right_hemi, right_hemi_file )

    # 1. STEP: run matrix generation
    SurfaceConnectivity.connect(input_file, scalarname, left_hemi_file, right_hemi_file, output_file )

    # 2. STEP: copy data to the proper output places
    shutil.copyfile( output_file, output )

    return output

#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Create a connectivity matrix of vertices. This required a TrackVis file with mapped vertices.' )

  entrypoint.add_input( 'i', 'input', 'The input TrackVis file.' )
  entrypoint.add_input( 'lh', 'left_hemi', 'The left hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'rh', 'right_hemi', 'The right hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'n', 'scalarname', 'The scalar name of mapped vertices.' )
  entrypoint.add_input( 'o', 'output', 'The output TrackVis file.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )

  a = FySurfaceConnectivity.run( options.input, options.left_hemi, options.right_hemi, options.scalarname, options.output, tempdir )

  sys.stdout = sys.__stdout__

  print 'Output matrix file: ', a
  print 'Done!'
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
