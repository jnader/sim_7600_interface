"""
This file contains GIS-related classes and functions.
TODO: Use logger
"""

import os
import geopandas as gpd
import webbrowser


class Zone:
    """
    Class abstracting a zone.
    It should be read from a shapefile (.shp) file.
    Currently, the only supported file format is .shp.
    I am not sure if other AutoCAD exported files can be supported.
    """

    shapefile_path: str = None
    zone_dataframe: gpd.GeoDataFrame = None
    zone_exploded = None
    zone_expanded = None
    zone_radius: int = None

    def __init__(self, shapefile: str, zone_radius: int = 50):
        """Constructor

        Args:
            shapefile (str): Path to shapefile .shp file.
            zone_radius (int, optional): Radius of the zone in meteres. Defaults to 50.
        """
        if "shp" not in os.path.splitext(shapefile)[1]:
            print("Only .shp file are supported")

        self.shapefile_path = shapefile

        if not os.path.exists(self.shapefile_path):
            print("File not found...")

    def read(self) -> bool:
        """Reads the shapefile provided in the constructor.

        Returns:
            bool: True if success, False otherwise
        """
        self.zone_dataframe = gpd.read_file(self.shapefile_path)
        if self.zone_dataframe is not None:
            # expand
            self.zone_exploded = self.zone_dataframe.explode()["geometry"]
            self.zone_expanded = self.zone_exploded.buffer(50)

            return True

        return False

    def explore(self) -> None:
        """Show zone on an interactive map"""
        if self.zone_dataframe is not None:
            map = self.zone_expanded.explore()
            map.save("/tmp/map.html")
            webbrowser.open("/tmp/map.html")

    def intersects(self, data_frame: gpd.GeoDataFrame) -> bool:
        """Test to check if data_frame is contained in zone.
        This will check if any point in data_frame is present
        inside the zone

        Args:
            data_frame (gpd.GeoDataFrame): GeoDataFrame to test.

        Returns:
            bool: True if data_frame contained in zone, False otherwise
        """
        return self.zone_dataframe.intersects(data_frame).any()


# if __name__ == "__main__":
#     zone = Zone("<.shp file>")

#     ret = zone.read()
