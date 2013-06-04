#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import nibabel
import numpy

# fyborg imports
import _actions
import config
from looper import Looper
from utility import Utility

class SurfaceConnectivity():
  '''
  Generate Surface Connectivity.
  '''

  @staticmethod
  def connect( fibers_file, scalar_name, lh_mesh_file, rh_mesh_file, output_matrix_file ):
    '''
    '''

    # load fibers file
    streamlines, header = nibabel.trackvis.read( fibers_file )

    # load surface files
    lh_verts, lh_faces = nibabel.freesurfer.read_geometry( lh_mesh_file )
    rh_verts, rh_faces = nibabel.freesurfer.read_geometry( rh_mesh_file )


    print header

    # check if the scalar_name exists
    scalar_names = header['scalar_name'].tolist()
    try:
      scalar_index = scalar_names.index( scalar_name )
    except:
      raise Exception( 'Scalar name was not found.' )
    
    #
    # HACK right now, also get the aparc+aseg index
    #
    aparc_aseg_index = scalar_names.index('aparc+aseg')
    # and configure an offset
    r_offset = len(lh_verts) 
    
    print 'allocating matrix with size ', str(len(lh_verts)+len(rh_verts))+'x'+str(len(lh_verts)+len(rh_verts))
    matrix = numpy.zeros([len(lh_verts)+len(rh_verts),len(lh_verts)+len(rh_verts)],numpy.dtype('uint8'))
    print 'allocated.'
    
    # now loop through the streamlines,
    # grab the mapped value,
    # increase the counter for the mapped value (and add the mapped value to the matrix before if it didn't exist)
    for sCounter, s in enumerate( streamlines[1] ):
      
      coordinates = s[0]
      scalars = s[1]

      start_point_scalar = scalars[0, scalar_index]
      end_point_scalar = scalars[-1, scalar_index]
      
      #
      # HACK right now, check which hemispheres the scalars map to
      #
      if scalars[0, aparc_aseg_index] >= 2000:
        # this is the right hemisphere
        start_point_scalar += r_offset
      if scalars[-1, aparc_aseg_index] >= 2000:
        # this is the right hemisphere
        end_point_scalar += r_offset
        
      # increase counter
      matrix[start_point_scalar, end_point_scalar] += 1
      
    # symmetrize
    matrix = matrix + matrix.T - numpy.diag( matrix.diagonal() )
    
    # and store them
    numpy.savetxt( output_matrix_file, matrix, delimiter="," )
      