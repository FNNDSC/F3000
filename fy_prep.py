#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyPrep():
  '''
  Prepare a diffusion DICOM directory by running quality control and generating a NII file.
  '''

  @staticmethod
  def run( options ):
    '''
    Runs the preparation stage.
    
    required inputs:
      options.diffusion_directory
      options.diffusion
      options.bvals
      options.bvecs
      options.qc_report
    '''

    # validate inputs
    if not os.path.exists( options.diffusion_directory ):
      raise Exception( 'Could not find the input dicom directory!' )

    # use a temporary workspace
    tempdir = options.tempdir
    # .. and copy all working files
    diffusion_directory = os.path.join( tempdir, os.path.basename( options.diffusion_directory ) )

    diffusion_nrrd_file = os.path.join( options.tempdir, 'diffusion.nrrd' )
    diffusion_QCed_nrrd_file = os.path.join( options.tempdir, 'diffusion_QCed.nrrd' )
    qc_report_file = os.path.join( options.tempdir, 'diffusion_QCReport.txt' )
    diffusion_file = os.path.join( tempdir, os.path.basename( options.diffusion ) )
    bvals_file = os.path.join( tempdir, os.path.basename( options.bvals ) )
    bvecs_file = os.path.join( tempdir, os.path.basename( options.bvecs ) )

    shutil.copytree( options.diffusion_directory, diffusion_directory )

    # 1. STEP: convert diffusion DICOMs to NRRD
    Preparation.diffusion2nrrd( diffusion_directory, diffusion_nrrd_file )

    # 2. STEP: run DTIPrep on the diffusion_nrrd_file
    Preparation.dtiprep( diffusion_nrrd_file )

    # 3. STEP: convert the quality-controlled diffusion_QCed_nrrd_file
    Preparation.nrrd2nii(diffusion_QCed_nrrd_file , diffusion_file, bvals_file, bvecs_file )

    # 4. STEP: copy data to the proper output places
    shutil.copyfile( diffusion_file, options.diffusion )
    shutil.copyfile( bvals_file, options.bvals )
    shutil.copyfile( bvecs_file, options.bvecs )
    shutil.copyfile( qc_report_file, options.qc_report )


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Prepare a diffusion DICOM directory by running quality control and generating a NII file.' )

  entrypoint.add_input( 'dir', 'diffusion_directory', 'The input diffusion DICOM directory.' )
  entrypoint.add_input( 'd', 'diffusion', 'The prepared output diffusion volume as a .NII.GZ file.' )
  entrypoint.add_input( 'bvals', 'bvals', 'The output bvals file.' )
  entrypoint.add_input( 'bvecs', 'bvecs', 'The output bvecs file.' )
  entrypoint.add_input( 'r', 'qc_report', 'The output quality control report.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  options.tempdir = Utility.setupEnvironment()

  FyPrep.run( options )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
