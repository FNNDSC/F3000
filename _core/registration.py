#
# FYBORG3000
#

# standard imports
import os, sys, subprocess, multiprocessing, time

# third-party imports
import nipy.algorithms.resample as resampler
import nipy
import dipy.align.aniso2iso as resampler2
import nibabel

# fyborg imports
import config
from utility import Utility

class Registration():
  '''
  Registration steps and related actions.
  '''

  @staticmethod
  def resample( input_file, target_file, output_file ):
    '''
    Resample the input image to match the target image.
    
    input_file
      the input file path
    target_file
      the target file path
    output_file
      the output file path    
    '''
    # load the input image
    input_image = nibabel.load( input_file )

    # load the target image
    target_image = nibabel.load( target_file )

    # configure the zooms
    old_zooms = input_image.get_header().get_zooms()[:3]
    new_zooms = target_image.get_header().get_zooms()[:3]

    # .. and the affine
    affine = input_image.get_affine()
    # .. and header
    header = input_image.get_header()

    # resample the input to match the target
    resampled_data, new_affine = resampler2.resample( input_image.get_data(), affine, old_zooms, new_zooms, 0 )

    # save the resampled image
    klass = input_image.__class__
    nibabel.save( klass( resampled_data, new_affine, header ), output_file )

  @staticmethod
  def register( input_file, target_file, output_directory ):
    '''
    Register the input image to match the target image using ANTs.
    
    input
      the input file path
    target
      the target file path
    output_directory
      the output directory
      
    The final output file is 2deformed.nii.gz in the output directory.
    '''

    output_prefix = os.path.join( output_directory, os.path.splitext( os.path.basename( input_file ) )[0] )

    # configure the ANTs environment
    cmd = 'export ANTSPATH=' + config.ANTS_BIN_DIR + ';'
    # change to ouput directory
    cmd += 'cd ' + output_directory + ';'
    # run ants.sh
    cmd += '$ANTSPATH/ants.sh 3 ' + target_file + ' ' + input_file + ' ' + output_prefix
    sp = subprocess.Popen( ["/bin/bash", "-i", "-c", cmd], bufsize=0, stdout=sys.stdout, stderr=sys.stderr )
    sp.communicate()

  @staticmethod
  def diffusion2structural( diffusion_file, structural_file, output_file, singleThread=False ):
    '''
    Register a diffusion scan to a structural scan.
    
    This process first splits the diffusion 4D image into components, upsamples each of them to match
    the structural. Then, all registered component images are merged back together. Finally,
    the upsampled and merged image is registered to the structural image and stored as the output_file.
    
    diffusion_file
      the diffusion image file path
    
    structural_file
      the structural image file path
    
    output_file
      the output file of the registered diffusion image
    
    singleThread
      optional flag to disable multithreading (default=False)
    '''

    # grab the diffusion_file basename
    diffusion_file_basename = os.path.basename( diffusion_file )
    diffusion_file_name = os.path.splitext( diffusion_file_basename )[0]
    diffusion_file_extension = os.path.splitext( diffusion_file_basename )[1]

    # we work in the directory of the output file
    working_directory = os.path.dirname( output_file )

    # define the sub-folders
    splitted_dir = os.path.join( working_directory, 'splitted' )
    resampled_dir = os.path.join( working_directory, 'resampled' )

    # create sub-folders
    if not os.path.exists( splitted_dir ):
      os.mkdir( splitted_dir )
    if not os.path.exists( resampled_dir ):
      os.mkdir( resampled_dir )

    #
    # 1. STEP: SPLIT 4D VOLUME
    #

    # split the 4D diffusion into its component images
    component_images = Registration.splitDiffusion( diffusion_file, splitted_dir )
    # component_images = nibabel.four_to_three( diffusion_image )

    #
    # 2. STEP: RESAMPLE ALL COMPONENT IMAGES (MULTITHREADED)
    #

    # specify the number of threads
    if singleThread:
      numberOfThreads = 1
    else:
      numberOfThreads = multiprocessing.cpu_count()

    # now split the list of the component_images into groups for each thread
    splitted_component_images = list( Utility.chunks( component_images, len( component_images ) / numberOfThreads + 1 ) )

    # list of threads
    t = [None] * len( splitted_component_images )

    # list of alive flags
    a = [None] * len( splitted_component_images )

    # loop through the chunks for each thread and start the threads
    for n, components in enumerate( splitted_component_images ):

      # mark thread as alive
      a[n] = True

      t[n] = multiprocessing.Process( target=Registration.resampleN, args=( components, structural_file, resampled_dir ) )
      t[n].start()

    allDone = False

    while not allDone:

      time.sleep( 1 )

      for n in xrange( len( splitted_component_images ) ):

        a[n] = t[n].is_alive()

      if not any( a ):
        # if no thread is alive
        allDone = True

    # here, all images were resampled

    #
    # 3. STEP: MERGE ALL RESAMPLED COMPONENT IMAGES
    #

    # let's merge them back together
    resampled_component_images = component_images

    for r in xrange( len( resampled_component_images ) ):
      resampled_component_images[r] = resampled_component_images[r].replace( 'splitted', 'resampled' )

    diffusion_resampled_merged_file_path = os.path.join( working_directory, diffusion_file_name + '_resampled' + diffusion_file_extension )

    merged_image = nibabel.concat_images( resampled_component_images )

    nibabel.save( merged_image, diffusion_resampled_merged_file_path )

    #
    # 4. STEP: REGISTER UPSAMPLED DIFFUSION TO STRUCTURAL SCAN
    #
