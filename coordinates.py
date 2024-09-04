"""
Handle GPS coordinates and reproject to different GIS systems.
"""

import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS, Transformer


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

    def __init__(
        self,
        time_utc: str,
        latitude: float,
        latitude_ind: str,
        longitude: float,
        longitude_ind: str,
    ):
        """Constructor

        Args:
            time_utc (str): String representing time in UTC format.
            latitude (float): Latitude of point
            latitude_ind (str): Latitude indicator: N/S
            longitude (float): Longitude of point
            longitude_ind (str): Longitude indicator E/W
        """
        # WGS84 Coordinate Reference System
        self.time_utc = time_utc
        self.latitude = latitude
        self.latitude_indicator = latitude_ind
        self.longitude = longitude
        self.longitude_indicator = longitude_ind
        self.crs_from = CRS.from_epsg(4326)

    def to_crs(self, crs_to: CRS, error: int = 10) -> gpd.GeoDataFrame:
        """Reproject current point to given Coordinate Reference System (CRS).

        Args:
            crs_to (CRS): Coordinate Reference System to project to.
            error (int): Error around the point to expand with.

        Returns:
            GeoDataFrame: Dataframe containing the new point
        """
        crs_to = CRS.from_epsg(crs_to)
        transformer = Transformer.from_crs(self.crs_from, crs_to)
        gps_point = Point(transformer.transform(self.latitude, self.longitude))

        d = {"time_utc": [self.time_utc], "geometry": [gps_point]}
        return gpd.GeoDataFrame(d, crs=crs_to).buffer(error)

    def __str__(self):
        """
        Special print() function for Coordinates class
        """
        return f"Time: {self.time_utc}, Lat: {self.latitude}{self.latitude_indicator}, Long: {self.longitude}{self.longitude_indicator}"
