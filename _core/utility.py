#
# FYBORG3000
#

# standard imports
import re, shutil, tempfile


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
  def setupEnvironment():
    '''
    Setup a F3000 temporary environment.

    Returns
      The temporary folder.
    '''
    return tempfile.mkdtemp( 'F3000', '', '/tmp' )

  @staticmethod
  def teardownEnvironment( tempdir ):
    '''
    Remove a F3000 temporary environment.
    
    tempdir
      The temporary folder to remove.
    '''
    shutil.rmtree( tempdir )


