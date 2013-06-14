#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, tempfile, time
from multiprocessing import Process

# third-party imports
import nibabel
import numpy

# fyborg imports
import _actions
import config
from utility import Utility

class LooperWithMatrix():
  '''
  Looping through fibers in a multithreaded fashion while performing actions.
  '''

  @staticmethod
  def loop( fibers_file, volume, lh_mesh_file, rh_mesh_file, neighbors, singleThread=False ):

    # load trk file
    s = nibabel.trackvis.read( fibers_file )
    tracks = s[0]

    # load meshes
    lh_verts, lh_faces = nibabel.freesurfer.read_geometry( lh_mesh_file )
    rh_verts, rh_faces = nibabel.freesurfer.read_geometry( rh_mesh_file )

    # load volume and get qForm matrix
    _image = nibabel.load( volume )
    qForm = _image.get_header().get_qform()
    qFormM = numpy.matrix( qForm )

    #
    # THREADED COMPONENT
    #
    if singleThread:
      numberOfThreads = 1
    else:
      numberOfThreads = 1#3#multiprocessing.cpu_count()

    print 'Splitting master into ' + str( numberOfThreads ) + ' pieces..'

    splittedOutputTracks = Utility.split_list( tracks[:], numberOfThreads )

    # list of threads
    t = [None] * numberOfThreads

    # list of alive flags
    a = [None] * numberOfThreads

    # list of matrix tempFiles
    mf = [None] * numberOfThreads


    for n in xrange( numberOfThreads ):

      # mark thread as alive
      a[n] = True

      # also create a temp file for the hdf5 file
      matrix_file = tempfile.mkstemp( '.h5', 'fyborg' )[1]

      mf[n] = matrix_file

      t[n] = Process( target=LooperWithMatrix._looper_, args=( splittedOutputTracks[n][:], lh_mesh_file, rh_mesh_file, int(neighbors), qFormM, matrix_file, n + 1 ) )
      print "Starting Thread-" + str( n + 1 ) + "..."
      t[n].start()

    allDone = False

    while not allDone:

      time.sleep( 1 )

      for n in xrange( numberOfThreads ):

        a[n] = t[n].is_alive()

      if not any( a ):
        # if no thread is alive
        allDone = True

    #
    # END OF THREADED COMPONENT
    #
    print "All Threads done!"
    #print mf

    return mf



  @staticmethod
  def _looper_( tracks, lh_mesh_file, rh_mesh_file, neighbors, qFormM, matrix_file, threadNumber ):
    '''
    Perform actions on subgroup of tracks.
    '''

    import numpy
    import nibabel
    import scipy
    import tables

    numberOfTracks = len( tracks )

    # load meshes
    lh_verts, lh_faces = nibabel.freesurfer.read_geometry( lh_mesh_file )
    rh_verts, rh_faces = nibabel.freesurfer.read_geometry( rh_mesh_file )
    leftVerticesRAS = []
    rightVerticesRAS = []

    # and convert vertices
    leftVertices = numpy.column_stack( ( lh_verts, numpy.ones( len( lh_verts ) ) ) )
    rightVertices = numpy.column_stack( ( rh_verts, numpy.ones( len( rh_verts ) ) ) )

    for l in leftVertices:
      leftVerticesRAS.extend( numpy.dot( qFormM.I, l ) )
    for r in rightVertices:
      rightVerticesRAS.extend( numpy.dot( qFormM.I, r ) )

    r_offset = len( lh_verts ) + 1

    leftVerticesRAS2 = []
    rightVerticesRAS2 = []

    for l in leftVerticesRAS:
      leftVerticesRAS2.append( l.tolist()[0][:-1] )

    for r in rightVerticesRAS:
      rightVerticesRAS2.append( r.tolist()[0][:-1] )

    # create KDTrees
    leftTree = scipy.spatial.KDTree( leftVerticesRAS2 )
    rightTree = scipy.spatial.KDTree( rightVerticesRAS2 )

    # create HDF5 matrix
    atom = tables.UInt8Atom()
    shape = ( len( lh_verts ) + len( rh_verts ), len( lh_verts ) + len( rh_verts ) )
    #filters = tables.Filters( complevel=5, complib='zlib' )
    h5f = tables.openFile( matrix_file, 'w' )
    matrix = h5f.createCArray( h5f.root, 'carray', atom, shape )


    # now loop through the tracks
    for tCounter, t in enumerate( tracks ):

      # some debug stats
      # c.debug( 'Thread-' + str( threadNumber ) + ': Processing ' + str( tCounter + 1 ) + '/' + str( numberOfTracks ), showDebug )
      print 'Thread-' + str( threadNumber ) + ': Processing ' + str( tCounter + 1 ) + '/' + str( numberOfTracks )

      # generate a unique ID for this track
      uniqueId = str( threadNumber ) + str( tCounter )

      coords = t[0]
      # scalars = t[1]


      # grab first and last coord
      first = coords[0]
      last = coords[-1]

      # FIRST POINT
      # check which surface vertex index is the closest to the first point
      # and use the lh and rh meshes to look this up
      first_left_distance_nn, first_left_index_nn = leftTree.query( first, neighbors )
      first_right_distance_nn, first_right_index_nn = rightTree.query( first, neighbors )

      # now for the LAST POINT
      # check which surface vertex index is the closest to the last point
      # and use the lh and rh meshes to look this up
      last_left_distance_nn, last_left_index_nn = leftTree.query( last, neighbors )
      last_right_distance_nn, last_right_index_nn = rightTree.query( last, neighbors )

      first_indices = []
      last_indices = []

      for i in range( neighbors ):
        # for each of the k points decide which one to use (left or right) based on the distance

        first_index = None
        last_index = None

        if first_right_distance_nn[i] < first_left_distance_nn[i]:
          # the right index is closer
          first_index = first_right_index_nn[i] + r_offset
        else:
          first_index = first_left_index_nn[i]

        first_indices.append( first_index )

        if last_right_distance_nn[i] < last_left_distance_nn[i]:
          # the right index is closer
          last_index = last_right_index_nn[i] + r_offset
        else:
          last_index = last_right_index_nn[i]

        last_indices.append( last_index )


      # now we have good values in first_indices and in last_indices
      # including the right offset if necessary

      for f in first_indices:
        for l in last_indices:

          # now increase the value in the matrix
          #print 'stored ', f, l
          matrix[f, l] += 1
          if f != l:  # for symmetry
            matrix[l, f] += 1

    # close the hdf5 file
    h5f.close()
