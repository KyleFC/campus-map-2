import React from 'react';
import MapComponent from './components/MapComponent';
import './App.css'
function App() {
  const position = [33.6540434, -117.8119295];
  return (
    <MapComponent position={position} />
  );
}

export default App;
