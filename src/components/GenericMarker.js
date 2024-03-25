import React,{useEffect,  useRef} from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const GenericMarker = ({ data, iconUrl, activeMarkerId }) => {
  const icon = L.icon({
    iconUrl: iconUrl || 'https://upload.wikimedia.org/wikipedia/commons/e/ed/Map_pin_icon.svg',
    iconSize: [20, 25],
    iconAnchor: [10,23]
  });

  const markerRef = useRef(null);

  useEffect(() => {
    if (activeMarkerId === data.id && markerRef.current) {
      markerRef.current.openPopup();
    }
  }, [activeMarkerId, data.id]);


  return (
    <Marker position={data.position} icon={icon} ref={markerRef}>
      <Popup>
        <div>
          <h3>{data.name}</h3>
          {data.category && <p>Category: {data.category}</p>}
          {data.description && <p>Description: {data.description}</p>}
          {data.image && <img src={data.image} alt={data.name} style={{ maxWidth: '200px' }} />}
        </div>
      </Popup>
    </Marker>
  );
};

export default GenericMarker;
