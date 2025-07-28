import React, { useEffect, useState } from 'react';

interface RecentLocationsProps {
  onSelect?: (location: string) => void;
  className?: string;
}

export const RecentLocations: React.FC<RecentLocationsProps> = ({ 
  onSelect,
  className = '' 
}) => {
  const [locations, setLocations] = useState<string[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('recentLocations');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setLocations(parsed.slice(0, 5));
      } catch (e) {
        console.error('Error parsing recent locations:', e);
      }
    }
  }, []);

  if (locations.length === 0) {
    return null;
  }

  return (
    <div className={`${className}`}>
      <label className="text-sm text-gray-600">Recent locations:</label>
      <div className="mt-1 flex flex-wrap gap-2">
        {locations.map((location, index) => (
          <button
            key={`${location}-${index}`}
            type="button"
            onClick={() => onSelect?.(location)}
            className="text-sm px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          >
            {location}
          </button>
        ))}
      </div>
    </div>
  );
};

// Utility function to add a location to recent locations
export const addToRecentLocations = (location: string) => {
  if (!location || location.trim() === '') return;
  
  try {
    const stored = localStorage.getItem('recentLocations');
    let locations: string[] = stored ? JSON.parse(stored) : [];
    
    // Remove duplicates and add new location at the beginning
    locations = [location, ...locations.filter(loc => loc !== location)];
    
    // Keep only the 10 most recent
    locations = locations.slice(0, 10);
    
    localStorage.setItem('recentLocations', JSON.stringify(locations));
  } catch (e) {
    console.error('Error saving to recent locations:', e);
  }
};

// Datalist component for HTML5 autocomplete
export const RecentLocationsDatalist: React.FC<{ id: string }> = ({ id }) => {
  const [locations, setLocations] = useState<string[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('recentLocations');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setLocations(parsed.slice(0, 5));
      } catch (e) {
        console.error('Error parsing recent locations:', e);
      }
    }
  }, []);

  return (
    <datalist id={id}>
      {locations.map((location, index) => (
        <option key={`${location}-${index}`} value={location} />
      ))}
    </datalist>
  );
};

// Hook for managing recent locations
export const useRecentLocations = () => {
  const [locations, setLocations] = useState<string[]>([]);

  useEffect(() => {
    const loadLocations = () => {
      const stored = localStorage.getItem('recentLocations');
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setLocations(parsed);
        } catch (e) {
          console.error('Error parsing recent locations:', e);
        }
      }
    };

    loadLocations();
    
    // Listen for storage changes from other tabs
    window.addEventListener('storage', loadLocations);
    return () => window.removeEventListener('storage', loadLocations);
  }, []);

  const addLocation = (location: string) => {
    addToRecentLocations(location);
    // Update local state
    setLocations(prev => [location, ...prev.filter(loc => loc !== location)].slice(0, 10));
  };

  const clearLocations = () => {
    localStorage.removeItem('recentLocations');
    setLocations([]);
  };

  return { locations, addLocation, clearLocations };
};