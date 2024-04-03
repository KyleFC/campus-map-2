import { useState, useEffect } from 'react';

const useLocationTracker = () => {
  const [currentLocation, setCurrentLocation] = useState(null);

  useEffect(() => {
    const trackLocation = () => {
      if (!navigator.geolocation) {
        console.error('Geolocation is not supported by this browser.');
        return;
      }

      navigator.geolocation.watchPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setCurrentLocation([latitude, longitude]);
        },
        (error) => {
          console.error('Error getting current location:', error);
        }
      );
    };

    trackLocation();
  }, []);

  return currentLocation;
};
export default useLocationTracker;