#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FySurfaceMap():
  '''
  Map Freesurfer vertices to a TrackVis file.
  '''

  @staticmethod
  def run( input, brain, left_hemi, right_hemi, k, decimate, output, tempdir ):
    '''
    Runs the mapping stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input fibers file!' )

    if not os.path.exists( brain ):
      raise Exception( 'Could not find the input brain file!' )

    if not os.path.exists( left_hemi ):
      raise Exception( 'Could not find the input left hemisphere surface file!' )

    if not os.path.exists( right_hemi ):
      raise Exception( 'Could not find the input right hemisphere surface file!' )

    # use a temporary workspace
    # .. and copy all working files
    input_file = os.path.join( tempdir, os.path.basename( input ) )
    brain_file = os.path.join( tempdir, os.path.basename( brain ) )
    identity_matrix_file = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'identity.xfm' )
    left_hemi_file = os.path.join( tempdir, os.path.basename( left_hemi ) )
    left_hemi_nover2ras_file = left_hemi_file + '.nover2ras'
    right_hemi_file = os.path.join( tempdir, os.path.basename( right_hemi ) )
    right_hemi_nover2ras_file = right_hemi_file + '.nover2ras'
    output_file = os.path.join( tempdir, os.path.basename( output ) )

    shutil.copy( input, input_file )
    shutil.copy( brain, brain_file )
    shutil.copy( left_hemi, left_hemi_file )
    shutil.copy( right_hemi, right_hemi_file )

    # 1. STEP: transform the input surfaces
    # no idea if we really need this..
    SurfaceMapping.transform( left_hemi_file, identity_matrix_file, left_hemi_nover2ras_file )
    SurfaceMapping.transform( right_hemi_file, identity_matrix_file, right_hemi_nover2ras_file )

    # 2. STEP: map the vertices
    SurfaceMapping.map( input_file, brain_file, left_hemi_nover2ras_file, right_hemi_nover2ras_file, output_file )

    # 3. STEP: copy data to the proper output places
    shutil.copyfile( output_file, output )

    return output, k

#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Map Freesurfer vertices to a TrackVis file.' )

  entrypoint.add_input( 'i', 'input', 'The input TrackVis file.' )
  entrypoint.add_input( 'b', 'brain', 'The brain scan as the reference space.' )
  entrypoint.add_input( 'lh', 'left_hemi', 'The left hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'rh', 'right_hemi', 'The right hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'k', 'k', 'The number of closest neighbors to map. NOT IMPLEMENTED YET! DEFAULT: 1', False, 1 )
  entrypoint.add_input( 'd', 'decimate', 'Surface decimation level to reduce the number of vertices. f.e. -d 0.333 reduces vertex count to 1/3. DEFAULT: 1.0 which means no decimation.', False, 1.0)
  entrypoint.add_input( 'o', 'output', 'The output TrackVis file.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )
    sys.stderr = open( os.devnull, 'wb' )

  a, b = FySurfaceMap.run( options.input, options.brain, options.left_hemi, options.right_hemi, options.k, options.decimate, options.output, tempdir )

  sys.stdout = sys.__stdout__
  sys.stderr = sys.__stderr__

  print 'Look-up Neighbors: ', str( b )
  print 'Output mapped TrackVis file: ', a
  print 'Done!'
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
