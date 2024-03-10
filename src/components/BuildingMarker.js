import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const BuildingMarker = ({ position, name, category, description, image }) => {
  const icon = L.icon({
    iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/e/ed/Map_pin_icon.svg',
    iconSize: [20, 25], // Set the size to 0x0 to make it invisible
  });
  return (
    <Marker position={position} icon={icon}>
      <Popup>
        <div>
          <h3>{name}</h3>
          <p>Category: {category}</p>
          <p>Description: {description}</p>
          {image && <img src={image} alt={name} style={{ maxWidth: '200px' }} />}
        </div>
      </Popup>
    </Marker>
  );
};

export default BuildingMarker;
