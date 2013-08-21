
class TC():


  def __init__(self):
    '''
    '''
    self.__points = {}
    self.__tracks = {}
    self.__all_points = []


  def add(self, track_id, x, y, z, v):
    '''
    '''
    # create point <-> track_id association
    if not x in self.__points:
      self.__points[x] = {}
    if not y in self.__points[x]:
      self.__points[x][y] = {}
    if not z in self.__points[x][y]:
      self.__points[x][y][z] = []
    self.__points[x][y][z].append(track_id)

    # index track points
    if not track_id in self.__tracks:
      self.__tracks[track_id] = []
    self.__tracks[track_id].append([x,y,z])

    # create a big cloud of all points without the track association
    self.__all_points.append(v)

  def find_track(self, x, y, z):
    '''
    '''
    try:
      return self.__points[x][y][z]
    except:
      return None

  def get_track(self, track_ids):
    '''
    '''

    tracks = {}

    for t in track_ids:
      tracks[t] = self.__tracks[t]

    return tracks

  def get_all_points(self):
    return self.__all_points

  def get_stats(self):
    print 'Tracks count:', len(self.__tracks.keys())
    print 'Total points:', len(self.__all_points*3)