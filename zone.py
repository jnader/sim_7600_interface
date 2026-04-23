"""
This file contains GIS-related classes and functions.
"""

import os
import geopandas as gpd
import webbrowser


class Zone:
    """Class abstracting a geographic zone loaded from a shapefile.

    Currently only .shp format is supported.
    """

    def __init__(self, shapefile: str, zone_radius: int = 1):
        """Constructor.

        Args:
            shapefile (str): Path to shapefile .shp file.
            zone_radius (int, optional): Buffer radius in metres. Defaults to 1.

        Raises:
            ValueError: If the file is not a .shp file.
            FileNotFoundError: If the file does not exist.
        """
        if os.path.splitext(shapefile)[1] != ".shp":
            raise ValueError(f"Only .shp files are supported, got: {shapefile}")
        if not os.path.exists(shapefile):
            raise FileNotFoundError(f"Shapefile not found: {shapefile}")

        self.shapefile_path = shapefile
        self.zone_radius = zone_radius
        self.zone_dataframe: gpd.GeoDataFrame = None
        self.zone_exploded = None
        self.zone_expanded = None

    def read(self) -> bool:
        """Reads the shapefile provided in the constructor.

        Returns:
            bool: True if success, False otherwise.
        """
        try:
            self.zone_dataframe = gpd.read_file(self.shapefile_path)
            self.zone_exploded = self.zone_dataframe.explode()["geometry"]
            self.zone_expanded = self.zone_exploded.buffer(self.zone_radius)
            return True
        except Exception as e:
            print(f"Failed to read shapefile: {e}")
            return False

    def explore(self) -> None:
        """Show zone on an interactive map."""
        if self.zone_expanded is not None:
            map_ = self.zone_expanded.explore()
            map_.save("/tmp/map.html")
            webbrowser.open("/tmp/map.html")

    def intersects(self, data_frame: gpd.GeoDataFrame) -> bool:
        """Test whether data_frame intersects the expanded zone.

        Args:
            data_frame (gpd.GeoDataFrame): GeoDataFrame to test.

        Returns:
            bool: True if data_frame intersects the zone, False otherwise.
        """
        if self.zone_expanded is None:
            raise RuntimeError("Zone not loaded. Call read() first.")
        return self.zone_expanded.intersects(data_frame).any()
