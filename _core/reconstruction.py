#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import dipy.core.gradients as gradienter
import dipy.data
import dipy.io
import dipy.reconst.dti as reconstructer
import dipy.tracking.eudx as tracker
import nibabel
import numpy

# fyborg imports
import config
from utility import Utility

class Reconstruction():
  '''
  Reconstruction steps and actions.
  '''

  @staticmethod
  def reconstruct( diffusion_file, bvals_file, bvecs_file, warped_segmentation_file, fa_file, adc_file, evecs_file ):
    '''
    Reconstruct a diffusion image by fitting a tensor model.
    
    diffusion_file
      the diffusion image file path to reconstruct
    bvals_file
      the b-value file path
    bvecs_file
      the b-vector file path
    warped_segmentation_file
      the segmentation/mask file path
    fa_file
      the fa map output file path
    adc_file
      the adc map output file path
    evecs_file
      the evecs map output file path
    '''
    # load the input image
    input_image = nibabel.load( diffusion_file )

    # grab the input data
    data = input_image.get_data()

    # create a simple mask
    #mask = data[..., 0] > 50
    
    # create a mask from the segmentation file 
    mask_image = nibabel.load( warped_segmentation_file ).get_data()
    mask = mask_image[...] > 0

    # load the bval and bvec files
    b_values, b_vectors = dipy.io.read_bvals_bvecs( bvals_file, bvecs_file )

    # create a gradient table
    gradient_table = gradienter.gradient_table_from_bvals_bvecs( b_values, b_vectors, 0, 10 )

    # instantiate tensor model
    tensor_model = reconstructer.TensorModel( gradient_table )

    print 'starting fiting..'
    # perform tensor fitting
    tensor_fitting = tensor_model.fit( data, mask )
    print 'ending fiting..'


    # create FA map
    fa_map = tensor_fitting.fa

    # clean-up FA map
    fa_map[numpy.isnan( fa_map )] = 0

    # create ADC map
    adc_map = tensor_fitting.md

    # clean-up ADC map
    adc_map[numpy.isnan( adc_map )] = 0

    # create eigenvector map
    evecs_map = tensor_fitting.evecs

    # store the maps
    nibabel.save( nibabel.Nifti1Image( fa_map, input_image.get_affine() ), fa_file )
    nibabel.save( nibabel.Nifti1Image( adc_map, input_image.get_affine() ), adc_file )
    nibabel.save( nibabel.Nifti1Image( evecs_map, input_image.get_affine() ), evecs_file )


  @staticmethod
  def streamlines( fa_file, evecs_file, fibers_file ):
    '''
    Generate streamlines from FA and EVECS maps and store a TrackVis file.
    
    fa_file
      the fa map file path
    evecs_file
      the evecs map file path
    fibers_file
      the TrackVis output file path
    '''

    # load the inputs
    fa_image = nibabel.load( fa_file )
    evecs_image = nibabel.load( evecs_file )

    fa_map = fa_image.get_data()
    evecs_map = evecs_image.get_data()

    # clean-up FA map
    fa_map[numpy.isnan( fa_map )] = 0

    # load evenly distributed sphere of 724 points
    sphere = dipy.data.get_sphere( 'symmetric724' )

    # apply the sphere for discretization
    peak_indices = reconstructer.quantize_evecs( evecs_map, sphere.vertices )

    # perform tracking
    print 'start tracking'
    tracking_results = tracker.EuDX( fa_map, peak_indices, seeds=1000000, odf_vertices=sphere.vertices, a_low=0.2 )
    streamlines = [streamline for streamline in tracking_results]
    print 'end tracking'

    # save as .TRK file
    trk_header = nibabel.trackvis.empty_header()
    # trk_header['voxel_size'] = fa_image.get_header().get_zooms()[:3]
    # trk_header['voxel_order'] = 'LPS'
    trk_header['dim'] = fa_map.shape
    trk_header['n_count'] = len(streamlines)

    # adjust trackvis header according to affine from FA
    nibabel.trackvis.aff_to_hdr( fa_image.get_affine(), trk_header, True, True )

    trk_tracks = ( ( sl, None, None ) for sl in streamlines )

    nibabel.trackvis.write( fibers_file, trk_tracks, trk_header, points_space='voxel' )
