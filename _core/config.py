#
# FYBORG3000
#

# the temporary directory where all data gets migrated before any calculation
TEMP_DIR = '/tmp'

# the external mri_convert tool
#  %source%
#    - the file to convert
#  %target%
#    - the output file
MRICONVERT_COMMAND = '. chb-fs stable; mri_convert %source% %target%'

# the external mris_transform tool
#  %surface%
#    - the surface file to transform 
#  %matrix%
#    - the transformation matrix file
#  %output_surface%
#    - the output surface file
#
MRISTRANSFORM_COMMAND = '. chb-fs stable; mris_transform %surface% %matrix% %output_surface%'

# the external mris_decimate tool
#  %decimation_level%
#    - the decimation leven 0..1
#  %surface%
#    - the input surface
#  %output_surface%
#    - the output surface
MRISDECIMATE_COMMAND = '. chb-fs stable; mris_decimate -d %decimation_level% %surface% %output_surface%'

# the external diffusion2nrrd tool
#  %diffusion_directory%
#    - the DICOM diffusion directory
#  %diffusion_nrrd%
#    - the converted nrrd output file
DIFFUSION2NRRD_COMMAND = 'DWIConvert --inputDicomDirectory %diffusion_directory% --outputVolume %diffusion_nrrd%'

# the external dti preparation tool
#  %diffusion_nrrd%
#    - the diffusion nrrd file
DTIPREP_COMMAND = 'DTIPrep -w %diffusion_nrrd% -c -d -p default.xml'

# the external nrrd2nii tool
#  %diffusion_nrrd%
#    - the diffusion nrrd file
#  %diffusion%
#    - the diffusion nii output file
#  %bvals%
#    - the bvals output file
#  %bvecs%
#    - the bvecs output file
NRRD2NII_COMMAND = 'DWIConvert --inputVolume %diffusion_nrrd% --outputVolume %diffusion% --outputBValues %bvals% --outputBVectors %bvecs% --conversionMode NrrdToFSL'

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
