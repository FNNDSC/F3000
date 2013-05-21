import numpy as np
from nibabel import load
import nibabel.trackvis as trk

from _core import *
import os
# filename = "DeterministicTractography/QBALLRecon/hardiO10.trk"
 
workdir='/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/clean'
 
trk_file = os.path.join(workdir, 'OUTORIG', 'tracks.trk')
trk_file_out = os.path.join(workdir, 'tracks_out.trk') 
diffusion_file = os.path.join(workdir, 'diffusion.nii.gz')
brain_file = os.path.join(workdir, 'brain.nii')
transform_file = os.path.join(workdir, 'OUT', 'diffusion_transform.txt')
 
trkfilename = trk_file#''
bfilename =  diffusion_file#"/software/data/STUT/DTI_TV/PWS04/dt_recon/lowb.nii"
mrfilename =  brain_file#"/software/data/MIBR/data/PWS04/head.nii"
 
reg = Utility.readITKtransform(transform_file)#np.genfromtxt('/software/data/STUT/DTI_TV/PWS04/dt_recon/register.dat',skiprows=4,comments='r')
 
bimg = load(bfilename)
mrimg = load(mrfilename)
M = np.array([[-1,0,0,128],
              [0, 0, 1, -128],
              [0, -1, 0, 128],
              [0,0,0,1]],dtype=float)
M1 = np.array([[-2,0,0,128],
              [0, 0, 2, -64],
              [0, -2, 0, 128],
              [0,0,0,1]],dtype=float)
 
#s = streamlines.Streamlines()
#s.loadTrk(trkfilename)
#s.printHeaderTrk()
 
trks = trk.read(trkfilename) 
tracks = trks[0]
hdr = trks[1]
 
aff = bimg.get_affine()
#xfm = np.dot(np.dot(np.dot(img2.get_affine(),np.linalg.inv(M)),reg),aff)
xfm = np.dot(mrimg.get_affine(),np.dot(np.linalg.inv(M),np.dot(np.linalg.inv(reg),M1)))
 
#s.affineTransform(np.dot(aff[0:3,0:3],np.diag(1./s.header['voxel_size'])),aff[0:3,3])
#trks.set_affine = (np.dot(xfm[0:3,0:3],np.diag(1./s.header['voxel_size'])),xfm[0:3,3])

#s.saveTrk(trk_file_out)
A = np.dot(aff[0:3,0:3],np.diag(1./hdr['voxel_size']))
print A
b = aff[0:3,3]

for t in xrange( len( tracks ) ):

  track = tracks[t]

  points = track[0]
  newPoints = np.copy( points )

  # loop through all points of the current track
  #for p in xrange( len( points ) ):


  xyz = points
  print xyz
  new_xyz = (np.dot(A, xyz.T) + b[:,None]).transpose()
  print new_xyz
  #newPoints[p] = new_xyz

  # create a new track with the transformed points
  newTrack = ( new_xyz, track[1], track[2] )

  # replace the old track with the newTrack
  tracks[t] = newTrack


trk_header = trk.empty_header()
# trk_header['voxel_size'] = fa_image.get_header().get_zooms()[:3]
# trk_header['voxel_order'] = 'LPS'
trk_header['dim'] = mrimg.shape

# adjust trackvis header according to affine from FA
trk.aff_to_hdr( mrimg.get_affine(), trk_header, True, True )

trk.write( trk_file_out, tracks, hdr, points_space='voxel' )
