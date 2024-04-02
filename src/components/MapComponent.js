import React, {useState} from 'react';
import { MapContainer, TileLayer, ZoomControl, Marker /*,ImageOverlay*/ } from 'react-leaflet';
import L from "leaflet";
import { MarkerData } from '../models/MarkerData';
import { Sidebar } from './SideBar';

import 'leaflet/dist/leaflet.css';

import GenericMarker from './GenericMarker';
import useLocationTracker from './useLocationTracker';
import buildingMarkers from '../data/markers.json';
import curr_location_icon from '../assets/icons/current_location_icon.png';

const MapComponent = ({ position }) => {

  //Convert buildingMarkers from JSON into MarkerData instances
  const markerDataObjects = buildingMarkers.map(marker => new MarkerData(
    marker.id,
    [marker.latitude, marker.longitude],
    marker.name,
    marker.category,
    marker.description,
    require(`../assets/images/${marker.image}`)
  ));

  const [categories, setCategories] = useState({
    buildings: true,
    housing: true,
    athletics: true
  });

  const [activeMarkerId, setActiveMarkerIdState] = useState(null);

  const setActiveMarkerId = (buildingId) => {
    setActiveMarkerIdState(buildingId);
  }

  const toggleCategory = (category) => {
    setCategories(prevCategories => ({
      ...prevCategories,
      [category]: !prevCategories[category],
    }));
  };
  
  const currentLocation = useLocationTracker();
  const icon = L.icon({
    iconUrl: curr_location_icon,
    iconSize: [25, 25],
    iconAnchor: [10,23]
  })

  return (
    <MapContainer 
    boundsOptions={{padding: [0, 50]}}
    center={position} 
    zoom={17} zoomControl={false} 
    style={{ height: '100vh', width: '100%' }}
    >
      
      <Sidebar
      categories={categories} 
      toggleCategory={toggleCategory} 
      buildings={buildingMarkers} 
      setActiveMarkerId={setActiveMarkerId}
      />
      <TileLayer url="https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png" />

      {markerDataObjects.map((data, index) => (
        categories[data.category] && (
        <GenericMarker
          key={index}
          data={data}
          activeMarkerId={activeMarkerId}
        />
        )
      ))}
      {currentLocation && (
        <Marker position={currentLocation} icon={icon}/>
      )}
      <ZoomControl position="topright" />
    </MapContainer>
  );
};

export default MapComponent;
