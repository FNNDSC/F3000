from fy_action import FyAction
import nibabel

class FyMapAction( FyAction ):

  def __init__( self, scalarName, volume ):
    """
    """
    super( FyMapAction, self ).__init__( scalarName )

    # load volume
    self._image = nibabel.load( volume )

    self._imageHeader = self._image.get_header()
    self._imageData = self._image.get_data()
    self._imageDimensions = self._imageData.shape[:3]
    self._imageSpacing = self._imageHeader.get_zooms()[:3]

  def scalarPerCoordinate( self, uniqueFiberId, x, y, z ):
    """
    """
    current = [ int( a / b ) for a, b in zip( [x, y, z], self._imageSpacing )]

    value = self._imageData[ min( current[0], self._imageDimensions[0] - 1 ), min( current[1], self._imageDimensions[1] - 1 ) , min( current[2], self._imageDimensions[2] - 1 )]

    return value
