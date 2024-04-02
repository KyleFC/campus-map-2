import React, { useState } from 'react';

const SearchBar = ({ buildings, setActiveMarkerId }) => {
    const [query, setQuery] = useState('');
    const [filteredBuildings, setFilteredBuildings] = useState([]);

    const handleInputChange = (e) => {
        const inputQuery = e.target.value;
        setQuery(inputQuery);

        if (!inputQuery.trim()) {
            setFilteredBuildings([]);
            return;
        }

        const matchedBuildings = buildings.filter((building) =>
            building.name.toLowerCase().includes(inputQuery.toLowerCase())
        );
        setFilteredBuildings(matchedBuildings);
    };

    return (
        <div class="search-container">
            <input
                type="text"
                value={query}
                onChange={handleInputChange}
                placeholder="Search for locations..."
                style={{ width: '100%', padding: '10px' }}
            />
            {query && (
                <ul class="dropdown" style={{listStyleType: 'none', padding: 0}}>
                    {filteredBuildings.map((building) => (
                        <li key={building.id} style={{padding: '5px'}}  onClick={() => setActiveMarkerId(building.id)}>
                            {building.name}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default SearchBar;
