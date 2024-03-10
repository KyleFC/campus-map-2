// MapComponent.js
import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, ImageOverlay } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import customMapOverlay from '../assets/images/osm2.png'; // Import your custom map overlay image
import buildingMarkers from '../data/markers.json';
import BuildingMarker from './BuildingMarker';

const MapComponent = ({ position}) => {
  const bounds = [[33.65109, -117.81465], [33.65694, -117.8064]]; // Adjust these bounds to fit your custom map overlay

  return (
    <MapContainer center={position} zoom={17} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <ImageOverlay url={customMapOverlay} bounds={bounds} />
      {buildingMarkers.map(marker => (
        <BuildingMarker
          key={marker.id}
          position={[marker.latitude, marker.longitude]}
          name={marker.name}
          category={marker.category}
          description={marker.description}
          image={require(`../assets/images/${marker.image}`)}
        />
      ))}
    </MapContainer>
  );
};

export default MapComponent;
