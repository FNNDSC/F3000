import tornado.ioloop
import tornado.web
import json
import numpy
import nibabel
import scipy.spatial
import sys
from tc import TC

class QueryHandler(tornado.web.RequestHandler):

  def initialize(self, querier):
    self.__querier = querier

  def get(self, id, radius, bundleradius):

    self.write(self.__querier.query(id, radius, bundleradius))

  def set_default_headers(self):
    self.set_header("Access-Control-Allow-Origin", "*")



class Querier():

  def __init__(self, trk, lh, rh, vol):

    # load files
    s = nibabel.trackvis.read(trk)
    tracks = s[0]

    # get the track transform
    t_m = s[1]['vox_to_ras']

    tracks_ras = []
    self.__track_trees = []
    # transform all tracks to RAS
    for t in tracks:
      points_ras = []
      for p in t[0]:

        # add 1.0 to the x,y,z coords
        p = p.tolist()
        p.append(1.0)
        # multiply with the transform
        points_ras.append(numpy.dot(t_m, numpy.array(p))[0:-1])
      
      # create kd tree for each fiber
      self.__track_trees.append(scipy.spatial.KDTree(points_ras))
      tracks_ras.append(points_ras)

    self.__tracks = tracks_ras

    # now index the tracks
    self.__TC = TC()
    for i,t in enumerate(self.__tracks):
      track_id = i
      for p in t:
        self.__TC.add(track_id, p[0], p[1], p[2], p)
    print 'tracks indexed'

    self._lh = nibabel.freesurfer.read_geometry(lh)
    self._rh = nibabel.freesurfer.read_geometry(rh)

    # we need to apply the c_ras value of the freesurfer mesh to transform to RAS
    cras = self.get_fsm_cras(lh)
    m_m = numpy.array([[1,0,0,float(cras[0])],[0,1,0,float(cras[1])],[0,0,1,float(cras[2])],[0,0,0,1]])

    lh_ras = []
    for l in self._lh[0]:
      l = l.tolist()
      l.append(1.0)

      lh_ras.append(numpy.dot(m_m, numpy.array(l))[0:-1])

    self._lh = lh_ras

    rh_ras = []
    for r in self._rh[0]:
      r = r.tolist()
      r.append(1.0)

      rh_ras.append(numpy.dot(m_m, numpy.array(r))[0:-1])

    self._rh = rh_ras    

    # create trees
    self.__lh_tree = scipy.spatial.KDTree( self._lh )
    self.__rh_tree = scipy.spatial.KDTree( self._rh )

    print 'meshes indexed'

    self.__all_points_tree = scipy.spatial.KDTree( self.__TC.get_all_points() )
    self.__all_points = self.__TC.get_all_points()

    print 'indexing completed'
    self.__TC.get_stats()





  def query(self, id, radius, bundleradius):

    print 'querying track', id

    # probe data
    points = self.__tracks[int(id)]

    first = points[0]
    last = points[-1]

    # FIRST POINT
    # check which surface vertex index is the closest to the first point
    # and use the lh and rh meshes to look this up
    first_indices_nn = self.__lh_tree.query_ball_point( first, int(radius) )
    first_right_indices_nn = self.__rh_tree.query_ball_point( first, int(radius) )

    # now for the LAST POINT
    # check which surface vertex index is the closest to the last point
    # and use the lh and rh meshes to look this up
    last_indices_nn = self.__lh_tree.query_ball_point( last, int(radius) )
    last_right_indices_nn = self.__rh_tree.query_ball_point( last, int(radius) )

    # grab coords for the first points
    first_coords = []
    for f in first_indices_nn:
      first_coords.append(self._lh[f].tolist())
    for f in first_right_indices_nn:
      first_coords.append(self._rh[f].tolist())


    last_coords = []
    for l in last_indices_nn:
      last_coords.append(self._lh[l].tolist())
    for l in last_right_indices_nn:
      last_coords.append(self._rh[l].tolist())

    track_points = []

    for t in points:
      track_points.append(t.tolist())

    # now get the neighborhood tracks
    print 'looking for neighborhood tracks'
    current_fiber_tree = self.__track_trees[int(id)] #scipy.spatial.KDTree( points )
    neighborhood = current_fiber_tree.query_ball_tree(self.__all_points_tree, float(bundleradius))
    

    # find the track for each point
    print 'map point to track'
    neighborhood_tracks = {}
    for t in neighborhood:
      for p in t:
        p = self.__all_points[p]
        nn_track_id = self.__TC.find_track(p[0], p[1], p[2])
        if nn_track_id:
          for nn in nn_track_id:
            if nn != int(id):
              neighborhood_tracks[nn] = nn

    print 'filter duplicates'

    print neighborhood_tracks

    # filter duplicates
    #neighborhood_tracks = set(neighborhood_tracks)

    print 'grab coordinates'
    neighborhood_tracks = self.__TC.get_track(neighborhood_tracks.keys())
    print 'done'

    # track_ids = []
    # for p in points:
    #   new_ids = self.__TC.find_track(p[0], p[1], p[2])
    #   track_ids.extend(new_ids)
    # print 'looking for neighborhood tracks done'
    # print set(track_ids)

    rval = {}
    rval['track_points'] = track_points
    rval['first_coords'] = first_coords
    rval['last_coords'] = last_coords
    rval['neighborhood'] = neighborhood_tracks

    return json.dumps(rval)

# start Querier
querier = Querier(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
print 'indexing complete'

application = tornado.web.Application([

    (r"/query/(?P<id>[^\/]+)/?(?P<radius>[^\/]+)/?(?P<bundleradius>[^\/]+)", QueryHandler, dict(querier=querier))

  ])


# start webserver
application.listen(8888)
tornado.ioloop.IOLoop.instance().start()

