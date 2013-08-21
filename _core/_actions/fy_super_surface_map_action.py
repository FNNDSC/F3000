from fy_action import FyAction
from fy_map_action import FyMapAction
import ctypes
import math
import numpy
import multiprocessing as mp
import nibabel
import scipy.spatial
import tables

class FySuperSurfaceMapAction( FyMapAction ):
  '''
  This action does not map anything to a TrackVis file but writes out a connectivity matrix.
  '''

  def __init__( self, scalarName, volume, leftMesh, rightMesh, matrixFile, radius ):
    super( FySuperSurfaceMapAction, self ).__init__( scalarName, volume )

    self._leftMesh = nibabel.freesurfer.read_geometry( leftMesh )
    self._rightMesh = nibabel.freesurfer.read_geometry( rightMesh )
    self._leftVerticesRAS = []
    self._rightVerticesRAS = []
    self._startVertices = {}
    self._endVertices = {}

    # transform the coords for the right and left hemisphere
    qForm = self._imageHeader.get_qform()
    qFormM = numpy.matrix( qForm )  # as matrix
    # extend the vertex coordinates with an element
    leftVertices = numpy.column_stack( ( self._leftMesh[0], numpy.ones( len( self._leftMesh[0] ) ) ) )
    rightVertices = numpy.column_stack( ( self._rightMesh[0], numpy.ones( len( self._rightMesh[0] ) ) ) )

    for l in leftVertices:
      self._leftVerticesRAS.extend( numpy.dot( qFormM.I, l ) )
    for r in rightVertices:
      self._rightVerticesRAS.extend( numpy.dot( qFormM.I, r ) )

    self._r_offset = len( self._leftMesh[0] )

    self._leftVerticesRAS2 = []
    self._rightVerticesRAS2 = []

    for l in self._leftVerticesRAS:
      self._leftVerticesRAS2.append( l.tolist()[0][:-1] )

    for r in self._rightVerticesRAS:
      self._rightVerticesRAS2.append( r.tolist()[0][:-1] )

    # create KDTrees
    self._leftTree = scipy.spatial.KDTree( self._leftVerticesRAS2 )
    self._rightTree = scipy.spatial.KDTree( self._rightVerticesRAS2 )

    # open the connectivity matrix file
#    atom = tables.UInt8Atom()
    self.__shape = ( len( leftVertices ) + len( rightVertices ), len( leftVertices ) + len( rightVertices ) )
#    self.__h5f = tables.openFile( matrixFile, 'w' )
#    self.__matrix = self.__h5f.createCArray( self.__h5f.root, 'carray', atom, shape )
    #self.__matrix = numpy.zeros(shape, dtype=numpy.uint16)
    self.__matrix = mp.Array(ctypes.c_ushort, self.__shape[0]*self.__shape[1])
    self.__matrix_file = matrixFile
    self.__neighbors = int( radius )

  def scalarPerFiber( self, uniqueFiberId, coords, scalars ):
    '''
    '''
    # image dimensions
    n1, n2, n3 = self._imageDimensions

    # grab first and last coord
    first = coords[0]
    last = coords[-1]

    # FIRST POINT
    # check which surface vertex index is the closest to the first point
    # and use the lh and rh meshes to look this up
    first_indices_nn = self._leftTree.query_ball_point( first, self.__neighbors )
    first_right_indices_nn = self._rightTree.query_ball_point( first, self.__neighbors )

    print first, last

    print 'first_indices', first_indices_nn, first_right_indices_nn

    # now for the LAST POINT
    # check which surface vertex index is the closest to the last point
    # and use the lh and rh meshes to look this up
    last_indices_nn = self._leftTree.query_ball_point( last, self.__neighbors )
    last_right_indices_nn = self._rightTree.query_ball_point( last, self.__neighbors )

    print 'last_indices', last_indices_nn, last_right_indices_nn

    # add the offset to all right hemisphere indices
    first_right_indices_nn = [v + self._r_offset for v in first_right_indices_nn]
    last_right_indices_nn = [v + self._r_offset for v in last_right_indices_nn]

    # now merge left and right indices for first and last point
    # since the right ones have an offset we can still distinguish later on
    first_indices_nn.extend(first_right_indices_nn)
    last_indices_nn.extend(last_right_indices_nn)

    # now we have good values in first_indices_nn and in last_indices_nn
    # including the right offset if necessary
    with self.__matrix.get_lock():
      
      arr = numpy.ctypeslib.as_array(self.__matrix.get_obj())
      m = arr.reshape(self.__shape)
      for f in first_indices_nn:
        for l in last_indices_nn:
          # now increase the value in the matrix
          
          print 'adding', f, l

          m[f, l] += 1
          if f != l:  # for symmetry
            m[l, f] += 1


    return FyAction.NoScalar

  def scalarPerCoordinate( self, uniqueFiberId, x, y, z ):
    '''
    '''
    return FyAction.NoScalar
  
  def close_file(self, left_hemi_file, right_hemi_file, left_curvature_output_file, right_curvature_output_file):
    '''
    '''
    m = numpy.ctypeslib.as_array(self.__matrix.get_obj())
    m = m.reshape(self.__shape)
    
    
    #here
    lh_vertices, lh_faces = nibabel.freesurfer.read_geometry( left_hemi_file )
    rh_vertices, rh_faces = nibabel.freesurfer.read_geometry( right_hemi_file )
    
    sum_vector = numpy.sum( m, axis=0 )

    import sys, os
    sys.path.append(os.path.join( os.path.dirname( __file__ ),'../'))
    from utility import Utility

    # write curvature files
    Utility.write_freesurfer_curvature( left_curvature_output_file, sum_vector[0:len( lh_vertices )] )
    Utility.write_freesurfer_curvature( right_curvature_output_file, sum_vector[len( lh_vertices ):] )  # here we start with the offset
    # end here
    print 'crv written!!! FTW!'
    
    numpy.save( self.__matrix_file, m)
    
    print 'stored matrix'
    
