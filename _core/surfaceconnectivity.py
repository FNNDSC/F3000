#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import nibabel
import numpy
import tables

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

    #print 'allocating matrix with size ', str( len( lh_verts ) + len( rh_verts ) ) + 'x' + str( len( lh_verts ) + len( rh_verts ) )
    # matrix = csc_matrix((len(lh_verts)+len(rh_verts)+1,len(lh_verts)+len(rh_verts)+1))

    atom = tables.UInt8Atom()
    shape = (len(lh_verts)+len(rh_verts),len(lh_verts)+len(rh_verts))
    filters = tables.Filters( complevel=5, complib='zlib' )
    h5f = tables.openFile( output_matrix_file, 'w' )
    matrix = h5f.createCArray( h5f.root, 'carray', atom, shape, filters=filters )

    #print 'allocated.'

    # now loop through the streamlines,
    # grab the mapped value,
    # increase the counter for the mapped value (and add the mapped value to the matrix before if it didn't exist)
    for sCounter, s in enumerate( streamlines ):

      coordinates = s[0]
      scalars = s[1]

      # subtract -1 since the first vertex is 1 and we need it to be 0
      start_point_scalar = scalars[0, scalar_index]-1
      end_point_scalar = scalars[-1, scalar_index]-1

      # increase counter
      matrix[start_point_scalar, end_point_scalar] += 1

      #print 'adding ', start_point_scalar, end_point_scalar, '   #',sCounter,'of', len(streamlines)
      
      # symmetrize
      if start_point_scalar != end_point_scalar:
        matrix[end_point_scalar, start_point_scalar] += 1

    # and store them
    h5f.close()

  @staticmethod
  def creature_curvature_files(matrix_file, left_hemi_file, right_hemi_file, left_curvature_output_file, right_curvature_output_file):
    '''
    '''
    
    # load the surfaces to compute the offsets correctly
    # as a reminder: the offset for the right hemisphere is the number of vertices in the left hemisphere
    # else-wise the vertex indices for right would start at 0 again
    lh_vertices, lh_faces = nibabel.freesurfer.read_geometry('/tmp/test123/lh.smoothwm.decimated')
    rh_vertices, rh_faces = nibabel.freesurfer.read_geometry('/tmp/test123/rh.smoothwm.decimated')
    
    # load the huge connectivity matrix
    h5f = tables.openFile(matrix_file)
    
    m = h5f.root.carray
    
    # sum along one axis (only one axis is fine since the matrix is symmetric)
    summed = numpy.sum(m, axis=0)

    # write curvature files
    Utility.write_freesurfer_curvature(left_curvature_output_file, summed[0:len(lh_vertices)]) 
    Utility.write_freesurfer_curvature(right_curvature_output_file, summed[len(lh_vertices):]) # here we start with the offset
        
    # close the hdf5 file
    h5f.close()
    