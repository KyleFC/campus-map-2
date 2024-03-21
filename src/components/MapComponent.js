import React, {useState} from 'react';

import { MapContainer, TileLayer /*,ImageOverlay*/ } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { MarkerData } from '../models/MarkerData';
import GenericMarker from './GenericMarker';
import useLocationTracker from './useLocationTracker';
import buildingMarkers from '../data/markers.json';

const MapComponent = ({ position }) => {
  //const [visibleMarkers, setVisibleMarkers] = useState({});
  const currentLocation = useLocationTracker();

  //Convert buildingMarkers from JSON into MarkerData instances
  const markerDataObjects = buildingMarkers.map(marker => new MarkerData(
    [marker.latitude, marker.longitude],
    marker.name,
    marker.category,
    marker.description,
    require(`../assets/images/${marker.image}`)
  ));

  const [categories, setCategories] = useState({
    building: true
  });

  const toggleCategory = (category) => {
    setCategories(prevCategories => ({
      ...prevCategories,
      [category]: !prevCategories[category],
    }));
  };

  const Sidebar = ({ categories, toggleCategory }) => {
    return (
      <div className="sidebar">
        {Object.keys(categories).map((category) => (
          <div key={category} className="category-item">
            <label>
              <input
                type="checkbox"
                checked={categories[category]}
                onChange={() => toggleCategory(category)}
              />
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </label>
          </div>
        ))}
      </div>
    );
  };

  //const bounds = [[33.65109, -117.81465], [33.65694, -117.8064]];
  //<ImageOverlay url={customMapOverlay} bounds={bounds} />
  return (
    <MapContainer center={position} zoom={17} style={{ height: '100vh', width: '100%' }}>
      <Sidebar categories={categories} toggleCategory={toggleCategory} />
      <TileLayer url="https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png" />
      

      {markerDataObjects.map((data, index) => (
        categories[data.category] && (
        <GenericMarker
          
          key={index}
          data={data}
        />
        )
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
