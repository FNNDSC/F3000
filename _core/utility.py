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


  @staticmethod
  def splitDiffusion( diffusion_file, output_directory ):
    '''
    Split a diffusion or other 4d image into its component images.
    
    diffusion_file
      the 4D input image
    output_directory
      the output directory to save the component images
    
    '''

    # load the diffusion image
    diffusion_image = nibabel.load( diffusion_file )
    diffusion_image_basename = os.path.basename( diffusion_file )
    diffusion_image_name = os.path.splitext( diffusion_image_basename )[0]
    diffusion_image_extension = os.path.splitext( diffusion_image_basename )[1]

    # split 4d diffusion image
    splitted_images = nibabel.four_to_three( diffusion_image )

    output_paths = []

    # save each of the splitted_images
    for number, image in enumerate( splitted_images ):
      component_output_path = os.path.join( output_directory, diffusion_image_name + str( number ) + diffusion_image_extension )
      nibabel.save( image, component_output_path )
      output_paths.append( component_output_path )

    # and return the file paths of the component images
    return output_paths
  
  
  @staticmethod
  def mergeDiffusion( diffusion_files, output_file ):
    '''
    Merge a list of diffusion files into one output_file.
    
    diffusion_files
      a list of diffusion file paths
    output_file
      the output file path
    '''

    diffusion_images = []

    # load all diffusion images
    for d in diffusion_files:
      diffusion_images.append( nibabel.load( d ) )

    # merge all diffusion images to one
    merged_image = nibabel.concat_images( diffusion_images )

    # store the image
    nibabel.save( merged_image, output_file )