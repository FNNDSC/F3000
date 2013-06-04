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
      self._leftVerticesRAS2.append(l.tolist()[0][:-1])

    for r in self._rightVerticesRAS:
      self._rightVerticesRAS2.append(r.tolist()[0][:-1])
    
    # create KDTrees
    self._leftTree = scipy.spatial.KDTree(self._leftVerticesRAS2)
    self._rightTree = scipy.spatial.KDTree(self._rightVerticesRAS2)

  def scalarPerFiber( self, uniqueFiberId, coords, scalars ):
    '''
    '''
    # image dimensions
    n1, n2, n3 = self._imageDimensions

    # grab first and last coord
    first = coords[0]
    last = coords[-1]

    vertexIndices = []

    for currentCoords in [first, last]:

      minVertexIndexLeft = None
      minDistanceLeft = float( 'inf' )
      minVertexIndexRight = None
      minDistanceRight = float( 'inf' )

      # check which surface point is the closest
      # .. for the left hemisphere
      
      print 'looking for closest point to ', currentCoords
      
      distance_nn, left_nn = self._leftTree.query(currentCoords)
      #left_index = self._leftVerticesRAS.index(left_nn)
      print 'KDTree found: vertex ', left_nn, ' : ', self._leftVerticesRAS2[left_nn], ' with distance ', distance_nn
      
      for index, l in enumerate( self._leftVerticesRAS2 ):
        #l = l.tolist()
        #distance = numpy.linalg.norm( currentCoords - [l[0][0], l[0][1], l[0][2]] )
        p1 = currentCoords
        p2 = l
        distance = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)
        #print currentCoords,l[0], distance
        if distance < minDistanceLeft:
          # .. grab its' vertex index
          minVertexIndexLeft = index
          minDistanceLeft = distance

      print 'Bruteforce found: vertex ', minVertexIndexLeft, ' : ', self._leftVerticesRAS[minVertexIndexLeft], ' with distance ', minDistanceLeft
      print '-------------'

#      # .. and for the right hemisphere
#      for index, l in enumerate( self._rightVerticesRAS ):
#        l = l.tolist()
#        distance = numpy.linalg.norm( currentCoords - [l[0][0], l[0][1], l[0][2]] )
#        if distance < minDistanceRight:
#          # .. grab its' vertex index
#          minVertexIndexRight = index + self._r_offset

      # and store it (either left or right, whichever is closer)
      if minDistanceRight < minDistanceLeft:
        vertexIndices.append( minVertexIndexRight )
      else:
        vertexIndices.append( minVertexIndexLeft )

    # now we have two vertex indicies, first the one of the start point, then the one of the end point
    self._startVertices[uniqueFiberId] = [[first[0], first[1], first[2]], vertexIndices[0]]
    self._endVertices[uniqueFiberId] = [[last[0], last[1], last[2]], vertexIndices[1]]

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
