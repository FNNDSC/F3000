#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyMap():
  '''
  Map scalar volumes to a TrackVis file.
  '''

  @staticmethod
  def run( input, volumes, output, tempdir ):
    '''
    Runs the mapping stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input fibers file!' )
    
    for v in volumes:
      if not os.path.exists( v ):
        raise Exception( 'Could not find the volume file ' + v + '!' )
    
    
    # use a temporary workspace
    # .. and copy all working files
    fibers_to_map_file = os.path.join( tempdir, os.path.basename( input ) )
    fibers_mapped_file = os.path.join( tempdir, os.path.basename( output ) )
    volumes_to_map = []
  
    shutil.copy(input, fibers_to_map_file)
    
    for v in options.volumes_to_map:
      v_file = os.path.join(tempdir, os.path.basename( v))
      shutil.copy(v, v_file)
      volumes_to_map.append(v_file)
      
    # 1. STEP: map all volumes
    Mapping.map(fibers_to_map_file, volumes_to_map, fibers_mapped_file)

    # 2. STEP: copy data to the proper output places
    shutil.copyfile( fibers_mapped_file, output )


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Map scalar volumes to a TrackVis file.' )

  entrypoint.add_input( 'i', 'input', 'The input TrackVis file.' )
  entrypoint.add_input_list( 'v', 'volumes_to_map', 'The scalar volumes to map as a list, f.e. -v adc.nii fa.nii e1.nii' )
  entrypoint.add_input( 'o', 'output', 'The output TrackVis file after mapping.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  FyMap.run( options.input, options.volumes_to_map, options.output, tempdir )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
