#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyCopyScalars():
  '''
  Copy scalars from one TrackVis file to another.
  '''

  @staticmethod
  def run( input, output, tempdir ):
    '''
    Runs the copying stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input TrackVis file!' )

    if not os.path.exists( output ):
      raise Exception( 'Could not find the output TrackVis file!' )

    Utility.copy_scalars( input, output, output )

    return True

#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Copy scalars from one TrackVis file to another.' )

  entrypoint.add_input( 'i', 'input', 'The source TrackVis file.' )
  entrypoint.add_input( 'o', 'output', 'The target TrackVis file.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )

  FyCopyScalars.run( options.input, options.output, tempdir )

  sys.stdout = sys.__stdout__

  print 'Done!'
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
