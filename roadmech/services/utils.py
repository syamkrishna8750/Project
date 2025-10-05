# services/utils.py
from math import radians, sin, cos, sqrt, atan2
import math

def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points 
    on the Earth (specified in decimal degrees) in kilometers.
    
    Returns:
        float: Distance in kilometers, or None if invalid coordinates
    """
    # Check for None values
    if None in [lat1, lon1, lat2, lon2]:
        return None
    
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

# Alternative implementation with error handling
def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Alternative implementation of Haversine formula with error handling.
    """
    try:
        # Check for valid coordinates
        if not all(isinstance(coord, (int, float)) for coord in [lat1, lon1, lat2, lon2]):
            return None
        
        # Earth radius in kilometers
        R = 6371.0
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
        
    except (TypeError, ValueError):
        return None

# You can use either function, but make sure to import the correct one
# For now, let's alias haversine_km to calculate_distance_km
haversine_km = calculate_distance_km