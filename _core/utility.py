#
# FYBORG3000
#

# standard imports
import os, re, shutil, subprocess, sys, tempfile

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


