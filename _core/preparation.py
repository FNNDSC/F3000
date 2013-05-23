#
# FYBORG3000
#

# standard imports
import os, shutil, sys, subprocess, multiprocessing, time

# third-party imports

# fyborg imports
import config
from utility import Utility

class Preparation():
  '''
  Preparation steps and actions (Quality Control).
  
  Inspired by https://gist.github.com/satra/5578926
  '''

  @staticmethod
  def diffusion2nrrd( diffusion_directory, diffusion_nrrd_file ):
    '''
    Parse a diffusion DICOM series and create a .NRRD.
    
    diffusion_directory
      the diffusion DICOM directory
    diffusion_nrrd_file
      the diffusion output file path
    '''

    # build the conversion command
    cmd = config.DIFFUSION2NRRD_COMMAND
    cmd = cmd.replace( '%diffusion_directory%', diffusion_directory )
    cmd = cmd.replace( '%diffusion_nrrd%', diffusion_nrrd_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()

  @staticmethod
  def nrrd2nii( diffusion_nrrd_file, diffusion_file, bvals_file, bvecs_file ):
    '''
    Convert a .NRRD diffusion file to .NII and create .bval- and .bvec-files.
    
    diffusion_nrrd_file
      the diffusion NRRD input file path
    diffusion_file
      the diffusion NII output file path
    bvals_file
      the bval-file output file path
    bvecs_file
      the bvec-file output file path
    '''

    # build the nrrd2nii command
    cmd = config.NRRD2NII_COMMAND
    cmd = cmd.replace( '%diffusion_nrrd%', diffusion_nrrd_file )
    cmd = cmd.replace( '%diffusion%', diffusion_file )
    cmd = cmd.replace( '%bvals%', bvals_file )
    cmd = cmd.replace( '%bvecs%', bvecs_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()


  @staticmethod
  def dtiprep( diffusion_nrrd_file ):
    '''
    Perform quality control on a diffusion scan.
    
    diffusion_nrrd_file
      the input nrrd file
      
    All outputs will appear in the folder of the input data.
    '''

    # build the dtiprep command
    cmd = config.DTIPREP_COMMAND
    cmd = cmd.replace( '%diffusion_nrrd%', diffusion_nrrd_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()
