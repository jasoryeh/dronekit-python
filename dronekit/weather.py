class Wind(object):
    """
    Wind information

    An object of this type is returned by :py:attr: `Vehicle.wind`.

    :param wind_direction: Wind direction in degrees
    :param wind_speed: Wind speed in m/s
    :param wind_speed_z: vertical wind speed in m/s
    """
    def __init__(self, wind_direction, wind_speed, wind_speed_z):
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.wind_speed_z = wind_speed_z

    def __str__(self):
        return "Wind: wind direction: {}, wind speed: {}, wind speed z: {}".format(self.wind_direction, self.wind_speed, self.wind_speed_z)
