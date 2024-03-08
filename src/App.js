import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, ImageOverlay } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import customMapOverlay from './osm2.png'; // Import your custom map overlay image

function App() {
  const position = [33.6540434, -117.8105295];
  const bounds = [[33.65109, -117.81465], [33.65694, -117.8064]]; // Adjust these bounds to fit your custom map overlay

  return (
    <MapContainer center={position} zoom={17} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <Marker position={position}>
        <Popup>
          Your university's name here. <br /> Easily customizable.
        </Popup>
      </Marker>
      <ImageOverlay url={customMapOverlay} bounds={bounds} />
    </MapContainer>
  );
}

export default App;
