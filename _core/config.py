#
# FYBORG3000
#

# the temporary directory where all data gets migrated before any calculation
TEMP_DIR = '/tmp'

# the external registration tool
#  %diffusion% 
#    - the diffusion file to register
#  %brain%
#    - the brain file
#  %matrix%
#    - the output .mat file
#  %warped_diffusion%
#    - the warped diffusion output file
REGISTRATION_COMMAND = 'fsl5.0-flirt -in %diffusion% -ref %brain% -out %warped_diffusion% -omat %matrix% -usesqform -nosearch -dof 6 -cost mutualinfo'

# the external warping/transforming tool
#  %segmentation%
#    - the segmentation label map to warp
#  %diffusion%
#    - the diffusion reference image
#  %inverse_matrix%
#    - the .mat file to use as a transform
#  %warped_segmentation%
#    - the warped output image
TRANSFORM_COMMAND = 'fsl5.0-flirt -in %segmentation% -ref %diffusion% -out %warped_segmentation% -init %inverse_matrix% -applyxfm -interp nearestneighbour'

# the external track transformation tool
#  %fibers%
#    - the input TrackVis file
#  %diffusion%
#    - the original diffusion volume
#  %brain%
#    - the original structural scan (target space)
#  %matrix%
#    - the registration matrix in .mat (FLIRT) format
#  %warped_fibers%
#    - the output TrackVis file
TRACK_TRANSFORM_COMMAND = 'track_transform %fibers% %warped_fibers% -src %diffusion% -ref %brain% -reg %matrix%'
