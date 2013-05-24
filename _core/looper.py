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

class Looper():
  '''
  Looping through fibers in a multithreaded fashion while performing actions.
  '''
  
  @staticmethod
  def loop(fibers_file, fibers_output_file, actions, singleThread=False):
  
    # load trk file
    s = nibabel.trackvis.read( fibers_file )
    tracks = s[0]
    origHeader = s[1]
    tracksHeader = numpy.copy( s[1] )
    numberOfScalars = origHeader['n_scalars']
    scalars = origHeader['scalar_name'].tolist()
    numberOfTracks = origHeader['n_count']
  
    # grab the scalarNames
    scalarNames = []
    for a in actions:
      if a.scalarName() != _actions.FyAction.NoScalar:
        scalarNames.append( a.scalarName() )
  
    # increase the number of scalars
    tracksHeader['n_scalars'] += len( scalarNames )
  
    # .. attach the new scalar names
    for i in range( len( scalarNames ) ):
      tracksHeader['scalar_name'][numberOfScalars + i] = scalarNames[i]
  
    #
    # THREADED COMPONENT
    #
    if singleThread:
      numberOfThreads = 1
    else:
      numberOfThreads = multiprocessing.cpu_count()
      
    print 'Splitting master into ' + str( numberOfThreads ) + ' pieces..' 
    
    splittedOutputTracks = Utility.split_list( tracks[:], numberOfThreads )
  
    # list of threads
    t = [None] * numberOfThreads
  
    # list of alive flags
    a = [None] * numberOfThreads
  
    # list of tempFiles
    f = [None] * numberOfThreads
  
    for n in xrange( numberOfThreads ):
      # configure actions
      __actions = []
      for act in actions:
        __actions.append( act )
  
      # mark thread as alive
      a[n] = True
      # fire the thread and give it a filename based on the number
      tmpFile = tempfile.mkstemp( '.trk', 'fyborg' )[1]
      f[n] = tmpFile
      t[n] = Process( target=Looper._looper_, args=( splittedOutputTracks[n][:], tracksHeader, tmpFile, __actions, n + 1 ) )
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
  
    #
    # Merging stage
    #
    print "Merging tracks.." 
  
    outputTracks = []
    # now read all the created tempFiles and merge'em to one
    for tmpFileNo in xrange( 0, len( f ) ):
      tTracks = nibabel.trackvis.read( f[tmpFileNo] )
  
      # add them
      outputTracks.extend( tTracks[0] )
  
    print "Merging done!" 
  
    nibabel.trackvis.write( fibers_output_file, outputTracks, tracksHeader )
  
    print "All done!" 


  @staticmethod
  def _looper_(tracks, tracksHeader, outputTrkFile, actions, threadNumber):
    '''
    Perform actions on a track.
    '''
  
    import numpy
    import nibabel
    import _actions
  
    numberOfTracks = len( tracks )
  
    # the buffer for the new tracks
    newTracks = []
  
    # now loop through the tracks
    for tCounter, t in enumerate( tracks ):
  
      # some debug stats
      #c.debug( 'Thread-' + str( threadNumber ) + ': Processing ' + str( tCounter + 1 ) + '/' + str( numberOfTracks ), showDebug )
      #print 'Thread-' + str( threadNumber ) + ': Processing ' + str( tCounter + 1 ) + '/' + str( numberOfTracks )
  
      # generate a unique ID for this track
      uniqueId = str( threadNumber ) + str( tCounter )
  
      tCoordinates = t[0]
      tScalars = t[1]
  
      # buffer for fiberScalars
      _fiberScalars = {}
  
      # first round: mapping per fiber
      # .. execute each action and buffer return value (scalar)
      for a in actions:
        value = a.scalarPerFiber( uniqueId, tCoordinates, tScalars )
        _fiberScalars[a.scalarName()] = value
  
      #
      # Coordinate Loop
      #
      # buffer for coordinate scalars)    
      scalars = []
  
      # second round: mapping per coordinate
      for cCounter, coords in enumerate( tCoordinates ):
  
        _coordScalars = {}
        _mergedScalars = [] # this is the actual buffer for ordered fiber and coord scalars merged together
  
        # .. execute each action and buffer return value (scalar)
        for a in actions:
          value = a.scalarPerCoordinate( uniqueId, coords[0], coords[1], coords[2] ) # pass x,y,z
          _coordScalars[a.scalarName()] = value
  
        # now merge the old scalars and the fiber and coord scalars
        # this preserves the ordering of the configured actions
        if tScalars != None:
          _mergedScalars.extend( tScalars[cCounter] )
  
        for a in actions:
          value = _fiberScalars[a.scalarName()]
          if value != _actions.FyAction.NoScalar:
            _mergedScalars.append( value )
          else:
            # no fiber scalar, check if there is a coord scalar
            value = _coordScalars[a.scalarName()]
            if value != _actions.FyAction.NoScalar:
              _mergedScalars.append( value )
  
        # attach scalars
        scalars.append( _mergedScalars )
  
      # validate the fibers using the action's validate methods
      validator = []
      for a in actions:
        validator.append( a.validate( uniqueId ) )
  
      if all( validator ):
        # this is a valid fiber
        # .. add the new track with the coordinates, the new scalar array and the properties
        newScalars = numpy.asarray( scalars )
        newTracks.append( ( t[0], newScalars, t[2] ) )
  
    # save everything
    nibabel.trackvis.write( outputTrkFile, newTracks, tracksHeader )
    