# Setting location
def set_location(latitude, longitude):
    Location.latitude = latitude
    Location.longitude = longitude


# Reset location
def reset_location():
    Location.latitude = 0
    Location.longitude = 0


# Check for emptiness
def emptiness_location():
    if Location.latitude != 0 or Location.longitude != 0:
        return True
    else:
        return False


# Class with location
class Location:
    latitude = 0
    longitude = 0
