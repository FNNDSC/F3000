function connectivity(data) {
  var result = JSON.parse(data);

  // remove old tracks
  if (QUERIER.connectivity.track) {
    ren3d.remove(QUERIER.connectivity.track);
    ren3d.remove(QUERIER.connectivity.last_lines);
    ren3d.remove(QUERIER.connectivity.first_lines);
  }


  track = new X.object();
  track.type = 'LINES';
  track.linewidth = 3;
  track.color = [0,0,1];
  var points_count = result['track_points'].length;
  track.points = new X.triplets(3 * points_count);
  track.normals = new X.triplets(3 * points_count);
  for(var i=0; i<points_count; i++) {
    var p = result['track_points'][i];
    track.points.add(p[0], p[1], p[2]);
    track.normals.add(0,0,0);
  }
  //track.transform.matrix = fibers.transform.matrix;
  ren3d.add(track);

  // get the track start point
  var first = result['track_points'][0];
  //first = X.matrix.multiplyByVector(fibers.transform.matrix, first[0], first[1], first[2]);

  // and the track end point
  var last = result['track_points'][result['track_points'].length-1];
  //last = X.matrix.multiplyByVector(fibers.transform.matrix, last[0], last[1], last[2]);

  // var mesh_inverse = X.matrix.identity();
  // X.matrix.invert(lh.transform.matrix, mesh_inverse);

  // first = X.matrix.multiplyByVector(mesh_inverse, first.xx, first.yy, first.zz);
  // last = X.matrix.multiplyByVector(mesh_inverse, last.xx, last.yy, last.zz);

  first_lines = new X.object();
  first_lines.type = 'LINES';
  first_lines.linewidth = 3;
  first_lines.pointsize = 10;
  first_lines.color = [0,0,1];
  points_count = result['first_coords'].length;
  first_lines.points = new X.triplets(6 * points_count);
  first_lines.normals = new X.triplets(6 * points_count);
  for(i=0;i<points_count;i++) {
    var p = result['first_coords'][i];
    first_lines.points.add(p[0], p[1], p[2]);
    first_lines.points.add(first[0], first[1], first[2]);

    first_lines.normals.add(0,0,0);
    first_lines.normals.add(0,0,0);
  }
  //first_lines.transform.matrix = lh.transform.matrix;
  ren3d.add(first_lines);

  last_lines = new X.object();
  last_lines.type = 'LINES';
  last_lines.linewidth = 3;
  last_lines.pointsize = 10;
  last_lines.color = [0,0,1];
  points_count = result['last_coords'].length;
  last_lines.points = new X.triplets(6 * points_count);
  last_lines.normals = new X.triplets(6 * points_count);
  for(i=0;i<points_count;i++) {
    var p = result['last_coords'][i];
    last_lines.points.add(p[0], p[1], p[2]);
    last_lines.points.add(last[0], last[1], last[2]);

    last_lines.normals.add(0,0,0);
    last_lines.normals.add(0,0,0);
  }
  //last_lines.transform.matrix = lh.transform.matrix;
  ren3d.add(last_lines);

  fibers.opacity = 0.2;


  QUERIER.connectivity.track = track;
  QUERIER.connectivity.first_lines = first_lines;
  QUERIER.connectivity.last_lines = last_lines;
  QUERIER.connectivity.id = result['track_id'];

  ren3d.resetBoundingBox();

  // hide the loading bar
  $('#loading').hide();

}

function bundles(data) {
  var result = JSON.parse(data);

  if (QUERIER.bundle.tracks) {
    for (n in QUERIER.bundle.tracks) {

      n = QUERIER.bundle.tracks[n];

      ren3d.remove(n);

    }
  }


  var neighborhood = [];
  for (var n in result['neighborhood']) {

    n = result['neighborhood'][n];


      nn = new X.object();
      nn.type = 'LINES';
      nn.linewidth = 3;
      nn.color = [1,0,0];
      var points_count = n.length;
      nn.points = new X.triplets(3 * points_count);
      nn.normals = new X.triplets(3 * points_count);
      for(var i=0; i<points_count; i++) {
        var p = n[i];
        nn.points.add(p[0], p[1], p[2]);
        nn.normals.add(0,0,0);
      }
      //track.transform.matrix = fibers.transform.matrix;
      ren3d.add(nn);
      neighborhood.push(nn);

  }

  QUERIER.bundle.tracks = neighborhood;

  ren3d.resetBoundingBox();

  // hide the loading bar
  $('#loading').hide();

}

