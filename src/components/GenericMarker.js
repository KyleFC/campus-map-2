import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const GenericMarker = ({ data, iconUrl }) => {
  const icon = L.icon({
    iconUrl: iconUrl || 'https://upload.wikimedia.org/wikipedia/commons/e/ed/Map_pin_icon.svg',
    iconSize: [20, 25],
    iconAnchor: [10,23]
  });

  return (
    <Marker position={data.position} icon={icon}>
      <Popup>
        <div>
          <h3>{data.name}</h3>
          <p>Category: {data.category}</p>
          <p>Description: {data.description}</p>
          {data.image && <img src={data.image} alt={data.name} style={{ maxWidth: '200px' }} />}
        </div>
      </Popup>
    </Marker>
  );
};

export default GenericMarker;
