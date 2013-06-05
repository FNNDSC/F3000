#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyWarpTracks():
  '''
  Warp a TrackVis file.
  '''

  @staticmethod
  def run( input, diffusion, brain, matrix, output, tempdir ):
    '''
    Runs the warping stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input fibers file!' )
    if not os.path.exists( diffusion ):
      raise Exception( 'Could not find the diffusion file!' )
    if not os.path.exists( brain ):
      raise Exception( 'Could not find the brain file!' )
    if not os.path.exists( matrix ):
      raise Exception( 'Could not find the matrix file!' )

    if not os.path.exists( output ):
      # create output directory
      os.mkdir( output )

    # use a temporary workspace
    # .. and copy all working files
    input_file = os.path.join( tempdir, os.path.basename( input ) )
    input_file_name = Utility.get_file_name( input_file )
    diffusion_file = os.path.join( tempdir, os.path.basename( diffusion ) )
    brain_file = os.path.join( tempdir, os.path.basename( brain ) )
    brain_file_name = Utility.get_file_name( brain_file )
    matrix_file = os.path.join( tempdir, os.path.basename( matrix ) )
    output_file = os.path.join( tempdir, input_file_name + '_to_' + brain_file_name + '.trk' )

    shutil.copyfile( input, input_file )
    shutil.copyfile( diffusion, diffusion_file )
    shutil.copyfile( brain, brain_file )
    shutil.copyfile( matrix, matrix_file )

    # 1. STEP: warp the data
    Registration.warp_fibers( input_file, diffusion_file, brain_file, matrix_file, output_file )

    # 2. STEP: store the warped output file in the output folder
    shutil.copy( output_file, output )

    return os.path.join( output, os.path.basename( output_file ) )

#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Warp (transform) a TrackVis file using a FLIRT registration matrix.' )

  entrypoint.add_input( 'i', 'input', 'The input TrackVis file.' )
  entrypoint.add_input( 'd', 'diffusion', 'The original diffusion volume.' )
  entrypoint.add_input( 'b', 'brain', 'The original structural scan.' )
  entrypoint.add_input( 'm', 'matrix', 'The FLIRT registration matrix.' )
  entrypoint.add_input( 'o', 'output', 'The output directory.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )

  a = FyWarpTracks.run( options.input, options.diffusion, options.brain, options.matrix, options.output, tempdir )

  sys.stdout = sys.__stdout__

  print 'Done!'
  print 'Output warped TrackVis file: ', a
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
