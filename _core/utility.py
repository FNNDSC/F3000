#
# FYBORG3000
#

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
