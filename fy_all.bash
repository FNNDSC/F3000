#!/bin/bash

echo "FYBORG3000 (c) FNNDSC, BCH 2013"

if [ -z "$3" ]
then
  echo "USAGE: `basename $0` {FREESURFER_DIR} {DIFFUSION_DICOM_DIR} {OUTPUT_DIR} [-v]"
  exit 1
fi

FREESURFER_DIR=$1
DIFFUSION_DICOM_DIR=$2
OUTPUT_DIR=$3

VERBOSE='-v'
if [ -z "$4" ]
then
  VERBOSE=''
fi

#
# GRAB STUFF FROM THE FREESURFER DIR
#
./fy_cherrypick_freesurfer.py -i $FREESURFER_DIR -o $OUTPUT_DIR $VERBOSE

#
# RUN DTI PREP
#
./fy_prep.py -i $DIFFUSION_DICOM_DIR -o $OUTPUT_DIR $VERBOSE

#
# REGISTER DIFFUSION TO T1
#
DIFFUSION_FILE=$OUTPUT_DIR/diffusion.nii.gz
BRAIN_FILE=$OUTPUT_DIR/brain.nii.gz
SEGMENTATION_FILE=$OUTPUT_DIR/aparc+aseg.nii.gz

./fy_register.py -i $DIFFUSION_FILE -i2 $SEGMENTATION_FILE -t $BRAIN_FILE -o $OUTPUT_DIR $VERBOSE

#
# RECONSTRUCT STREAMLINES
#
WARPED_SEGMENTATION_FILE=$OUTPUT_DIR/aparc+aseg_to_diffusion.nii.gz

./fy_reconstruct.py -i $DIFFUSION_FILE -m $WARPED_SEGMENTATION_FILE -o $OUTPUT_DIR $VERBOSE

#
# WARP STREAMLINES
#
FIBERS_FILE=$OUTPUT_DIR/fibers.trk
MATRIX_FILE=$OUTPUT_DIR/diffusion_to_brain.mat
FIBERS_TO_BRAIN_FILE=$OUTPUT_DIR/fibers_to_brain.trk

./fy_warptracks.py -i $FIBERS_FILE -d $DIFFUSION_FILE -b $BRAIN_FILE -m $MATRIX_FILE -o $FIBERS_TO_BRAIN_FILE $VERBOSE
 
#
# MAP SCALARS IN DIFFUSION SPACE
#
FIBERS_MAPPED_FILE=$OUTPUT_DIR/fibers_mapped.trk
ADC_FILE=$OUTPUT_DIR/adc.nii.gz
FA_FILE=$OUTPUT_DIR/fa.nii.gz

./fy_map.py -i $FIBERS_FILE -vol $ADC_FILE $FA_FILE -o $FIBERS_MAPPED_FILE $VERBOSE

#
# COPY SCALARS TO WARPED STREAMLINES
#
./fy_copyscalars.py -i $FIBERS_MAPPED_FILE -o $FIBERS_TO_BRAIN_FILE $VERBOSE

#
# MAP SCALARS IN T1 SPACE
#
FIBERS_TO_BRAIN_MAPPED_FILE=$OUTPUT_DIR/fibers_to_brain_mapped.trk

./fy_map.py -i $FIBERS_TO_BRAIN_FILE -vol $SEGMENTATION_FILE -o $FIBERS_TO_BRAIN_MAPPED_FILE $VERBOSE

#
# MAP SMOOTHWM VERTEX INDICES
#
LEFT_HEMI_FILE=$OUTPUT_DIR/lh.smoothwm
RIGHT_HEMI_FILE=$OUTPUT_DIR/rh.smoothwm
FIBERS_WITH_VERTICES_FILE=$OUTPUT_DIR/fibers_with_vertices.trk
DECIMATION_LEVEL=0.333

./fy_surfacemap.py -i $FIBERS_TO_BRAIN_MAPPED_FILE -b $BRAIN_FILE -lh $LEFT_HEMI_FILE -rh $RIGHT_HEMI_FILE -o $FIBERS_WITH_VERTICES_FILE -d $DECIMATION_LEVEL $VERBOSE

#
# SURFACE CONNECTIVITY
#
./fy_surfaceconnectivity.py -i $FIBERS_WITH_VERTICES -lh $LEFT_HEMI -rh $RIGHT_HEMI -n smoothwm -o $OUTPUT_DIR $VERBOSE
