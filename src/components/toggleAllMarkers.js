export const handleToggleAllMarkers = (buildingMarkers, visibleMarkers, setVisibleMarkers) => {
    const newVisibility = {};
  
    buildingMarkers.forEach(marker => {
      newVisibility[marker.id] = visibleMarkers;
    });
  
    setVisibleMarkers(newVisibility);
  };