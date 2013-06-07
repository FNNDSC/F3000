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
    shape = (len(lh_verts)+len(rh_verts)+1,len(lh_verts)+len(rh_verts)+1)
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

      start_point_scalar = scalars[0, scalar_index]
      end_point_scalar = scalars[-1, scalar_index]

      # increase counter
      matrix[start_point_scalar, end_point_scalar] += 1

      #print 'adding ', start_point_scalar, end_point_scalar, '   #',sCounter,'of', len(streamlines)
      
      # symmetrize
      if start_point_scalar != end_point_scalar:
        matrix[end_point_scalar, start_point_scalar] += 1

    # and store them
    h5f.close()
