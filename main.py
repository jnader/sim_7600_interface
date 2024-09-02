"""
Test script.
"""

from gps import Sim7600Module
from coordinates import Coordinates
from zone import Zone

def in_out_zone(flag):
    print(f'In/Out Zone {flag}')

if __name__ == "__main__":

    board = Sim7600Module()
    try:
        # Load the zone
        zone = Zone("./Blue_Line/Export_Output.shp")

        # Load GPS module
        board.open()
        if board.is_open:
            gps_module_position_epsg_4326: Coordinates
            gps_module_position_epsg_4326 = board.get_gps_position()
            gps_module_position_epsg_zone = gps_module_position_epsg_4326.to_crs(
                zone.zone_expanded.crs.to_epsg()
            )

            in_out_zone(zone.contains(gps_module_position_epsg_zone))

            board.close()

    except Exception as e:
        if board.is_open:
            board.close()
