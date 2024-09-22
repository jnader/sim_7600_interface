"""
Handle GPS coordinates and reproject to different GIS systems.
"""

import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS, Transformer
from utils import minute_to_degree


class Coordinates:
    """Basic class for storing lat/long GPS coordinates in EPSG-4326 CRS
    and reptojecting to different EPSG formats.
    """

    time_utc: str = None  # TODO: Use time.
    latitude: float = None
    latitude_indicator: str = None
    longitude: float = None
    longitude_indicator: str = None
    crs_from = None
    from_lbs: bool = False
    uncertainty: int = 50  # Uncertainty in meters (default for SIM7600: `AT+CGPSHOR?`)

    def __init__(
        self,
        time_utc: str,
        latitude: float,
        latitude_ind: str,
        longitude: float,
        longitude_ind: str,
        from_lbs: bool = False,
        uncertainty: int = 50,
    ):
        """Constructor

        Args:
            time_utc (str): String representing time in UTC format.
            latitude (float): Latitude of point
            latitude_ind (str): Latitude indicator: N/S
            longitude (float): Longitude of point
            longitude_ind (str): Longitude indicator E/W
            from_lbs (bool): Boolean to select if lat/long are specified in NMEA format
            uncertainty (int): Uncertainty on the position in meters (default is 10 meters)
        """
        # WGS84 Coordinate Reference System
        self.time_utc = time_utc
        self.latitude = latitude
        self.latitude_indicator = latitude_ind
        self.longitude = longitude
        self.longitude_indicator = longitude_ind
        self.crs_from = CRS.from_epsg(4326)
        self.uncertainty = uncertainty
        self.from_lbs = from_lbs
        if not self.from_lbs:
            self.nmea_to_coordinates()

    def nmea_to_coordinates(self) -> None:
        """Transforms latitude, longitude from NMEA Sentence format to real degrees.
        Latitude NMEA format: ddmm.mmmmmm
        Longitude NMEA format: dddmm.mmmm
        """
        latitude_nmea = float(self.latitude)
        longitude_nmea = float(self.longitude)

        self.latitude = latitude_nmea // 100
        self.longitude = longitude_nmea // 100

        latitude_minutes = latitude_nmea % 100
        longitude_minutes = longitude_nmea % 100

        self.latitude += minute_to_degree(latitude_minutes)
        self.longitude += minute_to_degree(longitude_minutes)

    def to_crs(self, crs_to: CRS) -> gpd.GeoDataFrame:
        """Reproject current point to given Coordinate Reference System (CRS).

        Args:
            crs_to (CRS): Coordinate Reference System to project to.

        Returns:
            GeoDataFrame: Dataframe containing the new point
        """
        crs_to = CRS.from_epsg(crs_to)
        transformer = Transformer.from_crs(self.crs_from, crs_to)
        gps_point = Point(transformer.transform(self.latitude, self.longitude))

        d = {"time_utc": [self.time_utc], "geometry": [gps_point]}
        return gpd.GeoDataFrame(d, crs=crs_to).buffer(self.uncertainty)

    def __str__(self):
        """
        Special print() function for Coordinates class
        """
        if self.latitude_indicator != "" and self.longitude_indicator != "":
            return f"Time: {self.time_utc}, Lat: {self.latitude}°{self.latitude_indicator}, Long: {self.longitude}°{self.longitude_indicator}, Uncertainty: {self.uncertainty}m"
        return f"Time: {self.time_utc}, Lat: {self.latitude}°, Long: {self.longitude}°, Uncertainty: {self.uncertainty}m"
