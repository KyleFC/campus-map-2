import React from 'react';
import { MapContainer, TileLayer, ImageOverlay } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import customMapOverlay from '../assets/images/osm2.png';
import { MarkerData } from '../models/MarkerData';
import GenericMarker from './GenericMarker'; // Assuming GenericMarker can accept MarkerData as prop
import useLocationTracker from './useLocationTracker';
import buildingMarkers from '../data/markers.json';

const MapComponent = ({ position }) => {
  const currentLocation = useLocationTracker();

  // Convert buildingMarkers from JSON into MarkerData instances
  const markerDataObjects = buildingMarkers.map(marker => new MarkerData(
    [marker.latitude, marker.longitude],
    marker.name,
    marker.category,
    marker.description,
    require(`../assets/images/${marker.image}`) // Assuming create-react-app's webpack config
  ));

  const bounds = [[33.65109, -117.81465], [33.65694, -117.8064]];

  return (
    <MapContainer center={position} zoom={17} style={{ height: '100vh', width: '100%' }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <ImageOverlay url={customMapOverlay} bounds={bounds} />

      {markerDataObjects.map((data, index) => (
        <GenericMarker
          key={index}
          data={data}
        />
      ))}

      {currentLocation && (
        <GenericMarker
          data={{position: currentLocation, name: "Your Location"}}
          iconUrl={"https://e7.pngegg.com/pngimages/772/529/png-clipart-google-maps-here-google-map-street-view-thumbnail.png"}
        />
      )}
    </MapContainer>
  );
};

export default MapComponent;
