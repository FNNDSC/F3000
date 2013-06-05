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
  def run( input, mask, output, tempdir ):
    '''
    Runs the reconstruction and streamlines stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the diffusion file!' )
    
    bvals = input.replace('.nii.gz', '.bvals')
    bvecs = input.replace('.nii.gz', '.bvecs')
    
    if not os.path.exists( bvals ):
      raise Exception( 'Could not find the bvals file!' )
    if not os.path.exists( bvecs ):
      raise Exception( 'Could not find the bvecs file!' )
    if not os.path.exists( mask ):
      raise Exception( 'Could not find the mask file!' )

    if not os.path.exists( output ):
      # create output directory
      os.mkdir( output )

    # use a temporary workspace
    # .. and copy all working files
    diffusion_file = os.path.join( tempdir, os.path.basename( input ) )
    bvals_file = os.path.join( tempdir, os.path.basename( bvals ) )
    bvecs_file = os.path.join( tempdir, os.path.basename( bvecs ) )
    mask_file = os.path.join( tempdir, os.path.basename( mask ) )

    shutil.copyfile( input, diffusion_file )
    shutil.copyfile( bvals, bvals_file )
    shutil.copyfile( bvecs, bvecs_file )
    shutil.copyfile( mask, mask_file )

    fa_file = os.path.join( tempdir, 'fa.nii.gz' )
    adc_file = os.path.join( tempdir, 'adc.nii.gz' )
    evecs_file = os.path.join( tempdir, 'evecs.nii.gz' )
    fibers_file = os.path.join( tempdir, 'fibers.trk' )

    # 1. STEP: reconstruct the data
    Reconstruction.reconstruct( diffusion_file, bvals_file, bvecs_file, mask_file, fa_file, adc_file, evecs_file )

    # 2. STEP: generate streamlines
    Reconstruction.streamlines( fa_file, evecs_file, fibers_file )

    # 3. STEP: store the outputs
    shutil.copy( fa_file, output )
    shutil.copy( adc_file, output )
    shutil.copy( evecs_file, output )
    shutil.copy( fibers_file, output )
    
    return os.path.join(output,os.path.basename(fa_file)), os.path.join(output,os.path.basename(adc_file)), os.path.join(output,os.path.basename(evecs_file)), os.path.join(output,os.path.basename(fibers_file))


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Reconstruct streamlines from a diffusion file.' )

  entrypoint.add_input( 'i', 'input', 'The original diffusion volume as a .NII.GZ file.' )
  entrypoint.add_input( 'm', 'mask', 'The mask to use (must be in diffusion space).')
  entrypoint.add_input( 'o', 'output', 'The output directory which includes the TrackVis file as well as FA-, ADC- and EVECS-volumes.')

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )

  a,b,c,d = FyReconstruct.run( options.input, options.mask, options.output, tempdir )

  sys.stdout = sys.__stdout__

  print 'Done!'
  print 'Output fa file: ', a
  print 'Output adc file: ', b
  print 'Output evecs file: ', c
  print 'Output TrackVis file: ', d
  print '-'*80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
