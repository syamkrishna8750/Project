from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="roadmech_app")   # set a descriptive user_agent
# RateLimiter prevents too many quick successive requests
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=2, error_wait_seconds=2)

def geocode_address(address):
    """Return (lat, lng) or (None, None)."""
    if not address:
        return None, None
    location = geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None
