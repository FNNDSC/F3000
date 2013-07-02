#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import nibabel
import numpy
import scipy.io as sio

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


    # check if the scalar_name exists
    scalar_names = header['scalar_name'].tolist()
    try:
      scalar_index = scalar_names.index( scalar_name )
    except:
      raise Exception( 'Scalar name was not found.' )

    print 'allocating matrix with size ', str( len( lh_verts ) + len( rh_verts ) ) + 'x' + str( len( lh_verts ) + len( rh_verts ) )

    matrix = numpy.zeros( (len( lh_verts ) + len( rh_verts ), len( lh_verts ) + len( rh_verts )), dtype=numpy.uint16 )
    print 'allocated.'

    # now loop through the streamlines,
    # grab the mapped value,
    # increase the counter for the mapped value (and add the mapped value to the matrix before if it didn't exist)
    for sCounter, s in enumerate( streamlines ):

      coordinates = s[0]
      scalars = s[1]

      # subtract -1 since the first vertex is 1 and we need it to be 0
      start_point_scalar = scalars[0, scalar_index]
      end_point_scalar = scalars[-1, scalar_index]

      # increase counter
      matrix[start_point_scalar, end_point_scalar] += 1

      # print 'adding ', start_point_scalar, end_point_scalar, '   #',sCounter,'of', len(streamlines)

      # symmetrize
      if start_point_scalar != end_point_scalar:
        matrix[end_point_scalar, start_point_scalar] += 1

    # save the matrix
    print 'storing matrix..'
    numpy.save( output_matrix_file, matrix)
    print 'matrix stored.'

  @staticmethod
  def create_curvature_files( matrix_file, left_hemi_file, right_hemi_file, left_curvature_output_file, right_curvature_output_file, manual=False ):
    '''
    '''

    # load the surfaces to compute the offsets correctly
    # as a reminder: the offset for the right hemisphere is the number of vertices in the left hemisphere
    # else-wise the vertex indices for right would start at 0 again
    lh_vertices, lh_faces = nibabel.freesurfer.read_geometry( left_hemi_file )
    rh_vertices, rh_faces = nibabel.freesurfer.read_geometry( right_hemi_file )

    # load the connectivity matrix
    #m = numpy.loadtxt( matrix_file, dtype=numpy.uint16 )
    m = numpy.load(matrix_file)

    sum_vector = numpy.sum( m, axis=0 )

    # write curvature files
    Utility.write_freesurfer_curvature( left_curvature_output_file, sum_vector[0:len( lh_vertices )] )
    Utility.write_freesurfer_curvature( right_curvature_output_file, sum_vector[len( lh_vertices ):] )  # here we start with the offset
