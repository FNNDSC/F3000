#
# FYBORG3000
#

import argparse, sys

class EntrypointArgParser( argparse.ArgumentParser ):
  '''
  Use our own parser to always show help on errors.
  '''
  def error( self, message ):
    '''
    '''
    print
    sys.stderr.write( 'ERROR: %s\n' % message )
    print
    self.print_help()
    sys.exit( 2 )

  def print_help( self ):
    '''
    '''
    print "FYBORG3000 (c) FNNDSC, BCH 2013"
    super( EntrypointArgParser, self ).print_help()


class Entrypoint( object ):
  '''
  A wrapper around the EntrypointArgParser to setup some defaults.
  '''
  def __init__( self, description ):
    '''
    '''
    self.__entrypoint = EntrypointArgParser( description )

    # add default verbose option
    self.add_flag( 'v', 'verbose', 'enable verbose output' )


  def add_flag( self, short, long, helpText, defaultSetting=False ):
    '''
    '''

    self.__entrypoint.add_argument( '-' + short, '--' + long, action='store_true', dest=long, default=defaultSetting, help=helpText )

  def add_input( self, short, long, helpText, requiredValue=True, defaultValue=None ):
    '''
    '''

    self.__entrypoint.add_argument( '-' + short, '--' + long, action='store', dest=long, default=defaultValue, help=helpText, required=requiredValue )

  def add_choices( self, name, choices_list, help_text, default_value ):
    '''
    '''
    self.__entrypoint.add_argument( name, choices=choices_list, help=help_text, default=default_value, nargs='?' )

  def add_input_list( self, short, long, helpText, defaultValue=None ):
    '''
    '''

    self.__entrypoint.add_argument( '-' + short, '--' + long, nargs='+', action='store', dest=long, default=defaultValue, help=helpText )

  def parse( self, args ):
    '''
    '''
    # always show the help if no arguments were specified
    if len( args ) == 1:
      self.__entrypoint.print_help()
      sys.exit( 1 )

    return self.__entrypoint.parse_args()
