import React,{useEffect,  useRef} from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import map_marker from '../assets/icons/map_marker.png'
const GenericMarker = ({ data, iconUrl, activeMarkerId }) => {
  const icon = L.icon({
    iconUrl: iconUrl || map_marker,
    iconSize: [20, 25],
    iconAnchor: [10,23]
  });

  const markerRef = useRef(null);

  useEffect(() => {
    if (activeMarkerId === data.id && markerRef.current) {
      markerRef.current.openPopup();
    }
  }, [activeMarkerId, data.id]);

/*{data.category && <p>Category: {data.category}</p>} */
  return (
    <Marker position={data.position} icon={icon} ref={markerRef}>
      <Popup>
        <div>
          <h3>{data.name}</h3>
          {data.image && <img src={data.image} alt={data.name} style={{ maxWidth: '200px' }} />}
          {data.description && <p>Description: {data.description}</p>}
        </div>
      </Popup>
    </Marker>
  );
};

export default GenericMarker;
