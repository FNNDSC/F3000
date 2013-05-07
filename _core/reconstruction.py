#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import dipy.core.gradients as gradienter
import dipy.io
import dipy.reconst.dti as reconstructer
import nibabel

# fyborg imports
import config
from utility import Utility

class Reconstruction():
  '''
  Reconstruction steps and actions.
  '''

  @staticmethod
  def reconstruct( diffusion_file, bval_file, bvec_file ):
    '''
    Resample the input image to match the target image.
    
    input_file
      the input file path
    target_file
      the target file path
    output_file
      the output file path
    '''
    # load the input image
    input_image = nibabel.load( input_file )

    # grab the input data
    data = input_image.get_data()

    # create a simple mask
    mask = data[..., 0] > 50

    # load the bval and bvec files
    b_values, b_vectors = dipy.io.read_bvals_bvecs( bval_file, bvec_file )

    # create a gradient table
    gradient_table = gradienter.gradient_table( b_values, b_vectors )

    # instantiate tensor model
    tensor_model = reconstructer.TensorModel( gradient_table )

    # perform tensor fitting
    tensor_fitting = tensor_model.fit( data, mask )
