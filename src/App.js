import React from 'react';
import MapComponent from './components/MapComponent';

function App() {
  const position = [33.6540434, -117.8105295];
  return (
    <MapComponent position={position} />
  );
}

export default App;
