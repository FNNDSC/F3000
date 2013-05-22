#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyRegister():
  '''
  Perform a registration between a diffusion and a structural image.
  
  Warp a segmentation along the way.
  '''

  @staticmethod
  def run( options ):
    '''
    Runs the resampling and registration stage.
    
    required inputs:
      options.diffusion
      options.brain
      options.segmentation
      options.matrix
      options.inverse_matrix
      options.warped_diffusion
      options.warped_segmentation
      options.smooth
    '''

    # validate inputs
    if not os.path.exists( options.diffusion ):
      raise Exception( 'Could not find the diffusion file!' )
    if not os.path.exists( options.brain ):
      raise Exception( 'Could not find the brain file!' )
    if not os.path.exists( options.segmentation ):
      raise Exception( 'Could not find the segmentation file!' )

    # use a temporary workspace
    tempdir = options.tempdir
    # .. and copy all working files
    diffusion_file = os.path.join( tempdir, os.path.basename( options.diffusion ) )
    diffusion_file_name = os.path.splitext( os.path.basename( diffusion_file ) )[0]
    # also strip any .nii if the extension was .nii.gz
    diffusion_file_name = diffusion_file_name.replace( '.nii', '' )
    brain_file = os.path.join( tempdir, os.path.basename( options.brain ) )
    segmentation_file = os.path.join( tempdir, os.path.basename( options.segmentation ) )
    resampled_file = os.path.join( tempdir, diffusion_file_name + '_resampled.nii.gz' )
    matrix_file = os.path.join( tempdir, os.path.basename( options.matrix ) )
    inverse_matrix_file = os.path.join( tempdir, os.path.basename( options.inverse_matrix ) )
    warped_segmentation_file = os.path.join( tempdir, os.path.basename( options.warped_segmentation ) )
    warped_diffusion_file = os.path.join( tempdir, os.path.basename( options.warped_diffusion ) )

    shutil.copyfile( options.diffusion, diffusion_file )
    shutil.copyfile( options.brain, brain_file )
    shutil.copyfile( options.segmentation, segmentation_file )

    if options.smooth:
      interpolation = 1  # trilinear interpolation
    else:
      interpolation = 0  # nearest-neighbor interpolation

    # 1. STEP: resample the data
    Registration.resample( diffusion_file, brain_file, resampled_file, interpolation )

    # 2. STEP: register the resampled file to the target file
    Registration.register( resampled_file, brain_file, matrix_file, warped_diffusion_file )

    # 3. STEP: create the inverse matrix
    Registration.invert_matrix( matrix_file, inverse_matrix_file )

    # 4. STEP: warp the segmentation
    Registration.warp( segmentation_file, diffusion_file, inverse_matrix_file, warped_segmentation_file )

    # 5. STEP: store the warped data and the registration matrices in the output folder
    shutil.copyfile( matrix_file, options.matrix )
    shutil.copyfile( inverse_matrix_file, options.inverse_matrix )
    shutil.copyfile( warped_segmentation_file, options.warped_segmentation )
    shutil.copyfile( warped_diffusion_file, options.warped_diffusion )


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Register a diffusion scan to a structural scan and warp a segmentation along the way.' )

  entrypoint.add_input( 'd', 'diffusion', 'The diffusion scan to warp.' )
  entrypoint.add_input( 'b', 'brain', 'The brain scan as the target space.' )
  entrypoint.add_input( 's', 'segmentation', 'The original segmentation.' )
  entrypoint.add_input( 'm', 'matrix', 'The matrix output path.' )
  entrypoint.add_input( 'im', 'inverse_matrix', 'The inverse matrix output path.' )
  entrypoint.add_input( 'wd', 'warped_diffusion', 'The warped diffusion output path.' )
  entrypoint.add_input( 'ws', 'warped_segmentation', 'The warped segmentation output path.' )
  entrypoint.add_flag( 's', 'smooth', 'Perform trilinear interpolation. DEFAULT: False', False )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  options.tempdir = Utility.setupEnvironment()

  FyRegister.run( options )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
