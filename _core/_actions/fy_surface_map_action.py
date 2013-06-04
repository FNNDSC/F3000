from fy_action import FyAction
from fy_map_action import FyMapAction
import math
import numpy
import nibabel
import scipy.spatial

class FySurfaceMapAction( FyMapAction ):

  def __init__( self, scalarName, volume, leftMesh, rightMesh ):
    super( FySurfaceMapAction, self ).__init__( scalarName, volume )

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

    self._r_offset = len( self._leftMesh[0] ) + 1

    self._leftVerticesRAS2 = []
    self._rightVerticesRAS2 = []

    for l in self._leftVerticesRAS:
      self._leftVerticesRAS2.append( l.tolist()[0][:-1] )

    for r in self._rightVerticesRAS:
      self._rightVerticesRAS2.append( r.tolist()[0][:-1] )

    # create KDTrees
    self._leftTree = scipy.spatial.KDTree( self._leftVerticesRAS2 )
    self._rightTree = scipy.spatial.KDTree( self._rightVerticesRAS2 )

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
    left_distance_nn, first_left_index_nn = self._leftTree.query( first )
    right_distance_nn, first_right_index_nn = self._rightTree.query( first )

    if right_distance_nn < left_distance_nn:
      # the right index is closer
      self._startVertices[uniqueFiberId] = [[first[0], first[1], first[2]], first_right_index_nn + self._r_offset]
    else:
      # the left index is closer
      self._startVertices[uniqueFiberId] = [[first[0], first[1], first[2]], first_left_index_nn]

    # now for the LAST POINT
    # check which surface vertex index is the closest to the last point
    # and use the lh and rh meshes to look this up
    left_distance_nn, last_left_index_nn = self._leftTree.query( last )
    right_distance_nn, last_right_index_nn = self._rightTree.query( last )

    if right_distance_nn < left_distance_nn:
      # the right index is closer
      self._endVertices[uniqueFiberId] = [[last[0], last[1], last[2]], last_right_index_nn + self._r_offset]
    else:
      # the left index is closer
      self._endVertices[uniqueFiberId] = [[last[0], last[1], last[2]], last_left_index_nn]

    return FyAction.NoScalar

  def scalarPerCoordinate( self, uniqueFiberId, x, y, z ):
    '''
    '''
    # read label values if we have matching coordinates
    startVertex = self._startVertices[uniqueFiberId]
    endVertex = self._endVertices[uniqueFiberId]

    if x == startVertex[0][0] and y == startVertex[0][1] and z == startVertex[0][2]:
      # this is the start point, so attach the start vertex
      return int( startVertex[1] )

    elif x == endVertex[0][0] and y == endVertex[0][1] and z == endVertex[0][2]:
      # this is the end point, so attach the end vertex
      return int( endVertex[1] )

    return -1  # else wise, return an empty scalar
