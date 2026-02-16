"""
Geocoding Utility - Address to Coordinates Conversion
Uses Nominatim (OpenStreetMap) API for free geocoding
"""

import requests
import time
from functools import lru_cache


class GeocodingService:
    """Handles geocoding and reverse geocoding operations"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            'User-Agent': 'BharatPropChain/1.0'  # Required by Nominatim
        }
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Nominatim rate limit: 1 req/sec
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    @lru_cache(maxsize=100)
    def geocode_address(self, address, city=None, state=None, country='India'):
        """
        Convert address to coordinates
        
        Args:
            address: Full address or partial address
            city: City name (optional)
            state: State name (optional)
            country: Country name (default: India)
        
        Returns:
            dict: {'lat': float, 'lng': float, 'display_name': str} or None
        """
        try:
            self._rate_limit()
            
            # Build search query
            query_parts = [address]
            if city:
                query_parts.append(city)
            if state:
                query_parts.append(state)
            query_parts.append(country)
            
            query = ', '.join(query_parts)
            
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'in'  # India only
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers=self.headers,
                timeout=5
            )
            
            if response.ok and response.json():
                result = response.json()[0]
                return {
                    'lat': float(result['lat']),
                    'lng': float(result['lon']),
                    'display_name': result.get('display_name', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    
    def reverse_geocode(self, lat, lng):
        """
        Convert coordinates to address
        
        Args:
            lat: Latitude
            lng: Longitude
        
        Returns:
            dict: Address components or None
        """
        try:
            self._rate_limit()
            
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json'
            }
            
            response = requests.get(
                f"{self.base_url}/reverse",
                params=params,
                headers=self.headers,
                timeout=5
            )
            
            if response.ok:
                result = response.json()
                address = result.get('address', {})
                return {
                    'display_name': result.get('display_name', ''),
                    'city': address.get('city') or address.get('town') or address.get('village', ''),
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'postcode': address.get('postcode', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            lat1, lng1: First coordinate
            lat2, lng2: Second coordinate
        
        Returns:
            float: Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Earth radius in kilometers
        R = 6371.0
        
        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)


# Global instance
geocoding_service = GeocodingService()


# Sample coordinates for major Indian cities (fallback)
CITY_COORDINATES = {
    'mumbai': {'lat': 19.0760, 'lng': 72.8777},
    'delhi': {'lat': 28.7041, 'lng': 77.1025},
    'bangalore': {'lat': 12.9716, 'lng': 77.5946},
    'bengaluru': {'lat': 12.9716, 'lng': 77.5946},
    'pune': {'lat': 18.5204, 'lng': 73.8567},
    'hyderabad': {'lat': 17.3850, 'lng': 78.4867},
    'chennai': {'lat': 13.0827, 'lng': 80.2707},
    'kolkata': {'lat': 22.5726, 'lng': 88.3639},
    'ahmedabad': {'lat': 23.0225, 'lng': 72.5714},
    'jaipur': {'lat': 26.9124, 'lng': 75.7873},
    'lucknow': {'lat': 26.8467, 'lng': 80.9462}
}


def get_city_coordinates(city_name):
    """Get coordinates for a city from fallback data"""
    city_lower = city_name.lower().strip()
    return CITY_COORDINATES.get(city_lower)
