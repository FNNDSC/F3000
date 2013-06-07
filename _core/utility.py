#
# FYBORG3000
#

# standard imports
import os, re, shutil, subprocess, sys, tempfile

# third-party imports
import nibabel
import numpy

# fyborg imports
import config

class Utility():
  '''
  Utility functions.
  '''

  @staticmethod
  def chunks( l, n ):
    '''
    Yield successive n-sized chunks from l.
    
    From: http://stackoverflow.com/a/312464/1183453
    '''
    for i in xrange( 0, len( l ), n ):
        yield l[i:i + n]

  @staticmethod
  def split_list( alist, wanted_parts=1 ):
    '''
    Split a list into wanted_parts.
    '''
    length = len( alist )
    return [ alist[i * length // wanted_parts: ( i + 1 ) * length // wanted_parts]
             for i in range( wanted_parts ) ]

  @staticmethod
  def natsort( l ):
    '''
    Sorts in a natural way.
    
    F.e. abc0 abc1 abc10 abc12 abc9 is sorted with python's sort() method
    This function would return abc0 abc1 abc9 abc10 abc12.
    
    From: http://stackoverflow.com/a/4836734/1183453
    '''
    convert = lambda text: int( text ) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert( c ) for c in re.split( '([0-9]+)', key ) ]
    return sorted( l, key=alphanum_key )


  @staticmethod
  def parseFreesurferDir( freesurfer_directory, brain_file, segmentation_file, lh_smoothwm_file, rh_smoothwm_file ):
    '''
    Scan a freesurfer directory for certain files, convert and copy them.
    '''

    # find relevant files in the freesurfer directory
    brain_file_orig = os.path.join( freesurfer_directory, 'mri', 'brain.mgz' )
    segmentation_file_orig = os.path.join( freesurfer_directory, 'mri', 'aparc+aseg.mgz' )
    lh_smoothwm_file_orig = os.path.join( freesurfer_directory, 'surf', 'lh.smoothwm' )
    rh_smoothwm_file_orig = os.path.join( freesurfer_directory, 'surf', 'rh.smoothwm' )

    # convert the brain_file_orig
    cmd = config.MRICONVERT_COMMAND
    cmd = cmd.replace( '%source%', brain_file_orig )
    cmd = cmd.replace( '%target%', brain_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()

    # convert the segmentation_file_orig
    cmd = config.MRICONVERT_COMMAND
    cmd = cmd.replace( '%source%', segmentation_file_orig )
    cmd = cmd.replace( '%target%', segmentation_file )

    sp = subprocess.Popen( ["/bin/bash", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()

    # copy the others
    shutil.copyfile( lh_smoothwm_file_orig, lh_smoothwm_file )
    shutil.copyfile( rh_smoothwm_file_orig, rh_smoothwm_file )


  @staticmethod
  def copy_scalars( trkFile1, trkFile2, outputFile ):
    '''
    Copy scalars from trkFile1 to trkFile2
    '''

    s = nibabel.trackvis.read( trkFile1 )
    s2 = nibabel.trackvis.read( trkFile2 )
    tracks = s[0]
    tracks2 = s2[0]
    origHeader = s[1]
    origHeader2 = s2[1]
    tracksHeader = numpy.copy( s[1] )
    tracksHeader2 = numpy.copy( s2[1] )

    # if tracksHeader['n_count'] != tracksHeader2['n_count']:
    #  c.error( 'The track counts do not match!' )
    #  sys.exit( 2 )

    # now copy
    tracksHeader2['n_scalars'] = tracksHeader['n_scalars']
    tracksHeader2['scalar_name'] = tracksHeader['scalar_name']

    newTracks2 = []

    for tCounter, t in enumerate( tracks ):

      tCoordinates = t[0]
      tScalars = t[1]

      # copy scalars over
      # tracks2[tCounter][1] = numpy.copy( tScalars )
      newTracks2.append( ( tracks2[tCounter][0], tScalars[:], tracks2[tCounter][2] ) )

    # write trkFile2 with update scalars
    nibabel.trackvis.write( outputFile, newTracks2, tracksHeader2 )

    print 'Copied Scalars!'


  @staticmethod
  def get_file_name( path ):
    '''
    Return the filename without extension of a given path.
    '''
    return os.path.splitext( os.path.basename( path ) )[0].replace( '.nii', '' )

  @staticmethod
  def setupEnvironment():
    '''
    Setup a F3000 temporary environment.

    Returns
      The temporary folder.
    '''
    return tempfile.mkdtemp( 'F3000', '', config.TEMP_DIR )


  @staticmethod
  def teardownEnvironment( tempdir ):
    '''
    Remove a F3000 temporary environment.
    
    tempdir
      The temporary folder to remove.
    '''
    shutil.rmtree( tempdir )

  @staticmethod
  def write_freesurfer_curvature( filename, values ):
    '''
    '''
    with open( filename, 'wb' ) as f:

      # magic number
      numpy.array( [255], dtype='>u1' ).tofile( f )
      numpy.array( [255], dtype='>u1' ).tofile( f )
      numpy.array( [255], dtype='>u1' ).tofile( f )

      # vertices number and two un-used int4
      numpy.array( [len( values )], dtype='>i4' ).tofile( f )
      numpy.array( [0], dtype='>i4' ).tofile( f )
      numpy.array( [1], dtype='>i4' ).tofile( f )

      # now the data
      numpy.array( values, dtype='>f4' ).tofile( f )


