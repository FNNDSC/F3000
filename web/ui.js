function create_ui() {
  
  var ui = new dat.GUI();
  
  var m_ui = ui.addFolder('Brain');
  m_ui.add(lh, 'opacity', 0, 1);
  m_ui.add(rh, 'opacity', 0, 1);
  m_ui.open();

  var c_ui = ui.addFolder('Connectivity');
  c_ui.add(QUERIER.connectivity, 'radius', 1, 30);
  c_ui.add(QUERIER.connectivity, 'id').listen();
  c_ui.open();

  var b_ui = ui.addFolder('Bundles');
  b_ui.add(QUERIER.bundle, 'radius', 0.1, 3);
  b_ui.add(QUERIER.bundle, 'grow bundle!');
  b_ui.open();

}