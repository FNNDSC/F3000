#!/usr/bin/python
import tornado.ioloop
import tornado.web
import sys
from web import *


# handler for connectivity
class ConnectivityHandler(tornado.web.RequestHandler):

  def initialize(self, querier):
    self.__querier = querier

  def get(self, X, Y, Z, radius):
    self.write(self.__querier.get_mesh_connectivity(X, Y, Z, radius))

  def set_default_headers(self):
    # enable CORS
    self.set_header("Access-Control-Allow-Origin", "*")

# handler for bundles (same as above but different function)
class BundleHandler(ConnectivityHandler):

  def initialize(self, querier):
    self.__querier = querier

  def get(self, id, radius):
    self.write(self.__querier.get_bundle(id, radius))
    
  def set_default_headers(self):
    # enable CORS
    self.set_header("Access-Control-Allow-Origin", "*")


#
#
#
# ENTRYPOINT
#
#
#

# simple sanity check
if len(sys.argv) != 5:
  print 'USAGE: ./fy_web.py TRK_FILE LH.SMOOTHWM RH.SMOOTHWM BRAIN.NII.GZ'
  sys.exit(1)

# start Querier
querier = Querier(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

application = tornado.web.Application([

    #
    # query a fiber with mesh connectivity using X,Y,Z coordinates (RAS space) 
    #
    (r"/connectivity/(?P<X>[^\/]+)/(?P<Y>[^\/]+)/(?P<Z>[^\/]+)/(?P<radius>[^\/]+)", ConnectivityHandler, dict(querier=querier)),

    #
    # query for neighborhood tracks using a track ID and a bundle radius
    #
    (r"/bundle/(?P<id>[^\/]+)/(?P<radius>[^\/]+)", BundleHandler, dict(querier=querier)),    

  ])

# start webserver
application.listen(8888)
tornado.ioloop.IOLoop.instance().start()
