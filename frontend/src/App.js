import React from 'react';
import MapComponent from './components/MapComponent';
import './App.css'
import NavBar from './components/NavBar';
function App() {
  const position = [33.6540434, -117.8119295];

  return (
    <div className="maincontainer">
      <NavBar />
      <MapComponent position={position} />
    </div>
  );
}

export default App;
