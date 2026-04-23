"""
Handle GPS coordinates and reproject to different GIS systems.
"""

import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS, Transformer


def minute_to_degree(minutes: float) -> float:
    return minutes / 60


class Coordinates:
    """Basic class for storing lat/long GPS coordinates in EPSG-4326 CRS
    and reprojecting to different EPSG formats.

    gps_status meaning:
      - 2: good GPS fix (outdoor, good satellite coverage)
      - 1: LBS positioning (less accurate, based on telecom towers)
      - 0: unusable (indoor, SIM not registered)
    """

    def __init__(
        self,
        time_utc: str = None,
        latitude: float = None,
        latitude_ind: str = None,
        longitude: float = None,
        longitude_ind: str = None,
        gps_status: int = 0,
        from_lbs: bool = False,
        uncertainty: int = 1000,
    ):
        self.time_utc = time_utc
        self.latitude = latitude
        self.latitude_indicator = latitude_ind
        self.longitude = longitude
        self.longitude_indicator = longitude_ind
        self.crs_from = CRS.from_epsg(4326)
        self.gps_status = gps_status
        self.uncertainty = uncertainty
        self.from_lbs = from_lbs

        if not self.from_lbs:
            self.nmea_to_coordinates()

    def nmea_to_coordinates(self) -> None:
        """Transforms latitude, longitude from NMEA format to decimal degrees.

        Latitude NMEA format:  ddmm.mmmmmm
        Longitude NMEA format: dddmm.mmmm
        """
        try:
            latitude_nmea = float(self.latitude)
            longitude_nmea = float(self.longitude)
        except (TypeError, ValueError):
            self.latitude = None
            self.longitude = None
            return

        self.latitude = latitude_nmea // 100 + minute_to_degree(latitude_nmea % 100)
        self.longitude = longitude_nmea // 100 + minute_to_degree(longitude_nmea % 100)

    def to_crs(self, crs_to: int) -> gpd.GeoDataFrame:
        """Reproject current point to given Coordinate Reference System (CRS).

        Args:
            crs_to (int): EPSG code to project to.

        Returns:
            GeoDataFrame: Buffered GeoDataFrame containing the reprojected point.
        """
        if self.latitude is None or self.longitude is None:
            raise ValueError("Cannot reproject: coordinates are None.")

        target_crs = CRS.from_epsg(crs_to)
        transformer = Transformer.from_crs(self.crs_from, target_crs, always_xy=True)
        x, y = transformer.transform(self.longitude, self.latitude)
        gps_point = Point(x, y)
        d = {"time_utc": [self.time_utc], "geometry": [gps_point]}
        return gpd.GeoDataFrame(d, crs=target_crs).buffer(self.uncertainty)

    def __str__(self):
        if self.latitude_indicator and self.longitude_indicator:
            return (
                f"Status: {self.gps_status}, Time: {self.time_utc}, "
                f"Lat: {self.latitude}°{self.latitude_indicator}, "
                f"Long: {self.longitude}°{self.longitude_indicator}, "
                f"Uncertainty: {self.uncertainty}m"
            )
        return (
            f"Status: {self.gps_status}, Time: {self.time_utc}, "
            f"Lat: {self.latitude}°, Long: {self.longitude}°, "
            f"Uncertainty: {self.uncertainty}m"
        )
