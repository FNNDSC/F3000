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
  def run( input, output, tempdir ):
    '''
    Runs the preparation stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input dicom directory!' )

    if not os.path.exists( output ):
      # create output directory
      os.mkdir( output )

    # use a temporary workspace
    # .. and copy all working files
    diffusion_directory = os.path.join( tempdir, os.path.basename( os.path.normpath( input ) ) )

    diffusion_nrrd_file = os.path.join( tempdir, 'diffusion.nrrd' )
    diffusion_QCed_nrrd_file = os.path.join( tempdir, 'diffusion_QCed.nrrd' )
    qc_report_file = os.path.join( tempdir, 'diffusion_QCReport.txt' )
    diffusion_file = os.path.join( tempdir, 'diffusion.nii.gz' )
    bvals_file = os.path.join( tempdir, 'diffusion.bvals' )
    bvecs_file = os.path.join( tempdir, 'diffusion.bvecs' )

    shutil.copytree( input, diffusion_directory )

    # 1. STEP: convert diffusion DICOMs to NRRD
    Preparation.diffusion2nrrd( diffusion_directory, diffusion_nrrd_file )

    # 2. STEP: run DTIPrep on the diffusion_nrrd_file
    Preparation.dtiprep( diffusion_nrrd_file )

    # 3. STEP: convert the quality-controlled diffusion_QCed_nrrd_file
    Preparation.nrrd2nii( diffusion_QCed_nrrd_file , diffusion_file, bvals_file, bvecs_file )

    # 4. STEP: copy data to the proper output places
    shutil.copy( diffusion_file, output )
    shutil.copy( bvals_file, output )
    shutil.copy( bvecs_file, output )
    shutil.copy( qc_report_file, output )

    return os.path.join( output, os.path.basename( diffusion_file ) ), os.path.join( output, os.path.basename( bvals_file ) ), os.path.join( output, os.path.basename( bvecs_file ) ), os.path.join( output, os.path.basename( qc_report_file ) )


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Prepare a diffusion DICOM directory by running quality control and generating a NII file.' )

  entrypoint.add_input( 'i', 'input', 'The input diffusion DICOM directory.' )
  entrypoint.add_input( 'o', 'output', 'The output directory including the prepared diffusion volume as a .NII.GZ file, bvals- and bvecs-files as well as the quality control report.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running..'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )
    sys.stderr = open( os.devnull, 'wb' )

  diffusion_file, bvals_file, bvecs_file, qc_report_file = FyPrep.run( options.input, options.output, tempdir )

  sys.stdout = sys.__stdout__
  sys.stderr = sys.__stderr__

  print 'Done!'
  print 'Output diffusion file: ', diffusion_file
  print 'Output bvals file: ', bvals_file
  print 'Output bvecs file: ', bvecs_file
  print 'Output qc_report file: ', qc_report_file
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
