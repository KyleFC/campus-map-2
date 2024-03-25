import React from 'react';
import SearchBar from './SearchBar';


export const Sidebar = ({categories, toggleCategory, buildings, setActiveMarkerId}) => {
    return (
      <div className="sidebar">
        
        <SearchBar buildings={buildings} setActiveMarkerId={setActiveMarkerId}/>
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