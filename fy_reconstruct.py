#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyReconstruct():
  '''
  Reconstruct streamlines from a diffusion file.
  '''

  @staticmethod
  def run( options ):
    '''
    Runs the reconstruction and streamlines stage.
    
    required inputs:
      options.diffusion
      options.bvals
      options.bvecs
      options.segmentation
      options.fa
      options.adc
      options.evecs
      options.fibers
    '''

    # validate inputs
    if not os.path.exists( options.diffusion ):
      raise Exception( 'Could not find the diffusion file!' )
    if not os.path.exists( options.bvals ):
      raise Exception( 'Could not find the bvals file!' )
    if not os.path.exists( options.bvecs ):
      raise Exception( 'Could not find the bvecs file!' )
    if not os.path.exists( options.segmentation ):
      raise Exception( 'Could not find the segmentation file!' )

    # use a temporary workspace
    tempdir = options.tempdir
    # .. and copy all working files
    diffusion_file = os.path.join( tempdir, os.path.basename( options.diffusion ) )
    bvals_file = os.path.join( tempdir, os.path.basename( options.bvals ) )
    bvecs_file = os.path.join( tempdir, os.path.basename( options.bvecs ) )
    segmentation_file = os.path.join( tempdir, os.path.basename( options.segmentation ) )

    shutil.copyfile( options.diffusion, diffusion_file )
    shutil.copyfile( options.bvals, bvals_file )
    shutil.copyfile( options.bvecs, bvecs_file )
    shutil.copyfile( options.segmentation, segmentation_file )

    fa_file = os.path.join( tempdir, os.path.basename( options.fa ) )
    adc_file = os.path.join( tempdir, os.path.basename( options.adc ) )
    evecs_file = os.path.join( tempdir, os.path.basename( options.evecs ) )
    fibers_file = os.path.join( tempdir, os.path.basename( options.fibers ) )

    # 1. STEP: reconstruct the data
    Reconstruction.reconstruct( diffusion_file, bvals_file, bvecs_file, segmentation_file, fa_file, adc_file, evecs_file )

    # 2. STEP: generate streamlines
    Reconstruction.streamlines( fa_file, evecs_file, fibers_file )

    # 3. STEP: store the outputs
    shutil.copyfile( fa_file, os.path.join( options.fa ) )
    shutil.copyfile( adc_file, os.path.join( options.adc ) )
    shutil.copyfile( evecs_file, os.path.join( options.evecs ) )
    shutil.copyfile( fibers_file, os.path.join( options.fibers ) )


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Reconstruct streamlines from a diffusion file.' )

  entrypoint.add_input( 'd', 'diffusion', 'The original diffusion volume.' )
  entrypoint.add_input( 'bvals', 'bvals', 'The bvals file.' )
  entrypoint.add_input( 'bvecs', 'bvecs', 'The bvecs file.' )
  entrypoint.add_input( 's', 'segmentation', 'The segmentation to use as a mask (must be in diffusion space).' )
  entrypoint.add_input( 'fa', 'fa', 'The fa output volume.' )
  entrypoint.add_input( 'adc', 'adc', 'The adc output volume.' )
  entrypoint.add_input( 'evecs', 'evecs', 'The evecs output volume.' )
  entrypoint.add_input( 'fibers', 'fibers', 'The output TrackVis file.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  options.tempdir = Utility.setupEnvironment()

  FyReconstruct.run( options )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
