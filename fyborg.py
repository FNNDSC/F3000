#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import os

# fyborg imports
from _core import *
from fy_register import FyRegister

workdir = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working'

options = lambda:0
options.input = os.path.join( workdir, 'diffusion.nii' )
options.target = os.path.join( workdir, 'brain.nii' )
options.output = os.path.join( workdir, 'F3001_out' )
options.smooth = False

# attach a temporary environment
options.tempdir = '/tmp/7AWDTyF3000'#Utility.setupEnvironment()

FyRegister.run( options )

# clean up temporary environment
#Utility.teardownEnvironment( options.tempdir )