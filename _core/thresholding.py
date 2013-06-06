#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import nibabel
import numpy

# fyborg imports
import _actions
import config
from looper import Looper
from utility import Utility

class Thresholding():
  '''
  Mapping of freesurfer surface vertex indices.
  '''

  @staticmethod
  def threshold( fibers_file, scalar_name, valid_values, output_fibers_file ):
    '''
    '''

    # load fibers file
    streamlines, header = nibabel.trackvis.read( fibers_file )

    # check if the scalar_name exists
    scalar_names = header['scalar_name'].tolist()
    try:
      scalar_index = scalar_names.index( scalar_name )
    except:
      raise Exception( 'Scalar name was not found.' )


    actions = [_actions.FyThresholdAction( scalar_index, valid_values )]

    # start the thresholding using the looper
    Looper.loop( fibers_file, output_fibers_file, actions )

  @staticmethod
  def threshold_by_label( fibers_file, scalar_name, label_file, offset, output_fibers_file ):
    '''
    '''

    # load the freesurfer label file
    vertices = nibabel.freesurfer.read_label( label_file )

    print offset
    print vertices

    # add offset
    vertices = [v + offset for v in vertices]

    print vertices

    # sort the vertices by using a set(..)
    Thresholding.threshold( fibers_file, scalar_name, set( vertices ), output_fibers_file )

