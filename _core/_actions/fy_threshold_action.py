from fy_action import FyAction

class FyThresholdAction( FyAction ):

  def __init__( self, scalar_index, valid_values ):
    super( FyThresholdAction, self ).__init__( FyAction.NoScalar )

    self.__scalar_index = scalar_index
    self.__valid_values = valid_values

    # buffer for valid fibers
    self.__valid_fibers = {}

  def scalarPerFiber( self, uniqueFiberId, coords, scalars ):
    '''
    '''
    first_scalar_value = scalars[0][self.__scalar_index]
    last_scalar_value = scalars[-1][self.__scalar_index]

    # flag this track as valid or invalid
    self.__valid_fibers[uniqueFiberId] = first_scalar_value in self.__valid_values or last_scalar_value in self.__valid_values

    return FyAction.NoScalar

  def validate( self, uniqueFiberId ):
    '''
    '''
    return self.__valid_fibers[uniqueFiberId]
