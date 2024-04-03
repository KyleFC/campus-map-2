import React from 'react';
import SearchBar from './SearchBar';
import { useMap } from 'react-leaflet';
import MartyChat from './MartyChat';
export const Sidebar = ({categories, toggleCategory, buildings, setActiveMarkerId}) => {
    const map = useMap();

    const disableMapInteraction = () => {
      map.dragging.disable();
      map.scrollWheelZoom.disable();
      if (map.tap) map.tap.disable(); // For mobile devices
      // Include any other interactions you want to disable
    };
  
    const enableMapInteraction = () => {
      map.dragging.enable();
      map.scrollWheelZoom.enable();
      if (map.tap) map.tap.enable(); // For mobile devices
      // Re-enable any other interactions you disabled
    };

  return (
      <div className="sidebar"
        onMouseEnter={disableMapInteraction}
        onMouseLeave={enableMapInteraction}
      >  
        <SearchBar buildings={buildings} setActiveMarkerId={setActiveMarkerId}/>
        {Object.keys(categories).map((category) => {
          const imagePath = require(`../assets/icons/${category}_icon.png`);
          return (
            <div key={category} className="category-item">
            <span className="image-placeholder">
              <img src={imagePath} alt={`${category} icon`} />
            </span>
            <label htmlFor={`checkbox-${category}`}>
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </label>
            <input
              id={`checkbox-${category}`}
              type="checkbox"
              checked={categories[category]}
              onChange={() => toggleCategory(category)}
            />
        </div>
        
        )})}
        <MartyChat />
      </div>
    );
  };