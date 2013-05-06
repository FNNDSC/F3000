#
# FYBORG3000
#

# standard imports
import shutil, tempfile


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
  def setupEnvironment():
    '''
    Setup a F3000 temporary environment.

    Returns
      The temporary folder.
    '''
    return tempfile.mkdtemp( 'F3000', '', '/tmp' )
  
  @staticmethod
  def teardownEnvironment(tempdir):
    '''
    Remove a F3000 temporary environment.
    
    tempdir
      The temporary folder to remove.
    '''
    shutil.rmtree( tempdir )
    