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
    input_file = os.path.join( tempdir, os.path.basename( input ) )
    input_file_name = Utility.get_file_name( input_file )
    output_file = os.path.join( tempdir, input_file_name + '_mapped.trk' )
    volumes_to_map = []

    shutil.copy( input, input_file )

    for v in volumes:
      v_file = os.path.join( tempdir, os.path.basename( v ) )
      shutil.copy( v, v_file )
      volumes_to_map.append( v_file )

    # 1. STEP: map all volumes
    Mapping.map( input_file, volumes_to_map, output_file )

    # 2. STEP: copy data to the output directory
    shutil.copyfile( output_file, output )

    return output


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Map scalar volumes to a TrackVis file.' )

  entrypoint.add_input( 'i', 'input', 'The input TrackVis file.' )
  entrypoint.add_input_list( 'vol', 'volume_to_map', 'The scalar volumes to map as a list, f.e. -v adc.nii fa.nii e1.nii' )
  entrypoint.add_input( 'o', 'output', 'The output TrackVis file.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )

  a = FyMap.run( options.input, options.volume_to_map, options.output, tempdir )

  sys.stdout = sys.__stdout__

  print 'Done!'
  print 'Output TrackVis file: ', a
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
