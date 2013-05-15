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

workdir2 = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working2'
cleandir = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/clean'


def stanford( workdir ):

  options = lambda:0
  options.input = os.path.join( workdir, 'HARDI150.nii.gz' )
  options.output = os.path.join( workdir, 'STANFORD' )
  options.diffusion = os.path.join( workdir, 'HARDI150.nii.gz' )
  options.bvals = os.path.join( workdir, 'HARDI150.bval' )
  options.bvecs = os.path.join( workdir, 'HARDI150.bvec' )
  options.fa = os.path.join( options.output, 'fa.nii.gz' )
  options.evecs = os.path.join( options.output, 'evecs.nii.gz' )

  return options

def testdata( workdir ):

  options = lambda:0
  options.input = os.path.join( workdir, 'diffusion.nii' )
  options.output = os.path.join( workdir, 'WORKINGVERSION' )
  options.diffusion = os.path.join( workdir, 'diffusion.nii' )
  options.bvals = os.path.join( workdir, 'diffusion.mghdti.bvals' )
  options.bvecs = os.path.join( workdir, 'diffusion.mghdti.bvecs' )
  options.fa = os.path.join( options.output, 'fa.nii.gz' )
  options.evecs = os.path.join( options.output, 'evecs.nii.gz' )

  return options

def testdata2( workdir ):

  options = lambda:0
  options.input = os.path.join( workdir, 'diffusion.nii.gz' )
  options.output = os.path.join( workdir, 'WORKINGVERSIONNEW' )
  options.diffusion = os.path.join( workdir, 'diffusion.nii.gz' )
  options.bvals = os.path.join( workdir, 'diffusion.bval' )
  options.bvecs = os.path.join( workdir, 'diffusion.bvec' )
  options.fa = os.path.join( options.output, 'fa.nii.gz' )
  options.evecs = os.path.join( options.output, 'evecs.nii.gz' )

  return options

def testdata3( workdir ):

  options = lambda:0
  options.input = os.path.join( workdir, 'F3000', 'diffusion_warped.nii.gz' )
  options.output = os.path.join( workdir, 'WORKINGVERSIONREG' )
  options.diffusion = os.path.join( workdir, 'F3000', 'diffusion_warped.nii.gz' )
  options.bvals = os.path.join( workdir, 'diffusion.bval' )
  options.bvecs = os.path.join( workdir, 'diffusion.bvec' )
  options.fa = os.path.join( options.output, 'fa.nii.gz' )
  options.evecs = os.path.join( options.output, 'evecs.nii.gz' )

  return options

def clean1(workdir):
  options = lambda:0
  options.input = os.path.join( workdir, 'diffusion.nii.gz' )
  options.target = os.path.join( workdir, 'brain.nii' )
  options.output = os.path.join( workdir, 'OUT' )
  options.smooth = False
  options.tempdir = Utility.setupEnvironment()
  
  print options.tempdir
  
  return options

def clean2(workdir):
  options = lambda:0
  options.input = os.path.join( workdir, 'OUT', 'diffusion_registered.nii.gz' )
  options.output = os.path.join( workdir, 'OUT2' )
  if not os.path.exists(options.output):
    os.mkdir(options.output)
  options.diffusion = options.input
  options.bvals = os.path.join( workdir, 'diffusion.bval' )
  options.bvecs = os.path.join( workdir, 'diffusion.bvec' )
  options.fa = os.path.join( options.output, 'fa.nii.gz' )
  options.evecs = os.path.join( options.output, 'evecs.nii.gz' )

  return options
  
  
# registration
options = clean1( cleandir )
FyRegister.run(options)

options = clean2(cleandir)

# reconstruction
Reconstruction.reconstruct( options.diffusion, options.bvals, options.bvecs, options.output )
Reconstruction.streamlines( options.fa, options.evecs, os.path.join( options.output, 'tracks.trk' ) )
