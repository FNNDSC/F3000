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
  def run( options ):
    '''
    Runs the mapping stage.
    
    required inputs:
      options.fibers_to_map
      options.brain
      options.lh_smoothwm
      options.rh_smoothwm
      options.fibers_mapped
    '''

    # validate inputs
    if not os.path.exists( options.fibers ):
      raise Exception( 'Could not find the input fibers file!' )

    if not os.path.exists( options.lh_smoothwm ):
      raise Exception( 'Could not find the input left hemisphere surface file!' )

    if not os.path.exists( options.rh_smoothwm ):
      raise Exception( 'Could not find the input right hemisphere surface file!' )


    # use a temporary workspace
    tempdir = options.tempdir
    # .. and copy all working files
    fibers_to_map_file = os.path.join( tempdir, os.path.basename( options.fibers_to_map ) )
    brain_file = os.path.join( tempdir, os.path.basename( options.brain ) )
    identity_matrix_file = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'identity.xfm' )
    lh_smoothwm_file = os.path.join( tempdir, os.path.basename( options.lh_smoothwm ) )
    lh_smoothwm_nover2ras_file = lh_smoothwm_file + '.nover2ras'
    rh_smoothwm_file = os.path.join( tempdir, os.path.basename( options.rh_smoothwm ) )
    rh_smoothwm_nover2ras_file = rh_smoothwm_file + '.nover2ras'
    fibers_mapped_file = os.path.join( tempdir, os.path.basename( options.fibers_mapped ) )

    shutil.copy( options.brain, brain_file )
    shutil.copy( options.fibers_to_map, fibers_to_map_file )
    shutil.copy( options.lh_smoothwm, lh_smoothwm_file )
    shutil.copy( options.rh_smoothwm, rh_smoothwm_file )

    # 1. STEP: transform the input surfaces
    SurfaceMapping.transform( lh_smoothwm_file, identity_matrix_file, lh_smoothwm_nover2ras_file )
    SurfaceMapping.transform( rh_smoothwm_file, identity_matrix_file, rh_smoothwm_nover2ras_file )

    # 2. STEP: map the vertices
    SurfaceMapping.map( fibers_to_map_file, brain_file, lh_smoothwm_nover2ras_file, rh_smoothwm_nover2ras_file, fibers_mapped_file )

    # 3. STEP: copy data to the proper output places
    shutil.copyfile( fibers_mapped_file, options.fibers_mapped )


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Map Freesurfer vertices to a TrackVis file.' )

  entrypoint.add_input( 'f', 'fibers_to_map', 'The input TrackVis file.' )
  entrypoint.add_input( 'b', 'brain', 'The brain scan as the reference space.' )
  entrypoint.add_input( 'lh', 'lh_smoothwm', 'The left hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'rh', 'rh_smoothwm', 'The right hemisphere Freesurfer surface.' )
  entrypoint.add_input( 'fm', 'fibers_mapped', 'The output TrackVis file after mapping.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  options.tempdir = Utility.setupEnvironment()

  FySurfaceMap.run( options )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
