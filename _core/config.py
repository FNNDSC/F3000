#
# FYBORG3000
#

# the temporary directory
TEMP_DIR = '/tmp'

# the external registration tool
#  %diffusion% 
#    - the diffusion file to register
#  %brain%
#    - the brain file
#  %matrix%
#    - the output .mat file
REGISTRATION_COMMAND = 'fsl5.0-flirt -in %diffusion% -ref %brain% -omat %matrix% -usesqform -nosearch -dof 6 -cost mutualinfo'

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
