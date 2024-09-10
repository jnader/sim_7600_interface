"""
Utility functions for sending AT commands and handling responses.
"""

import Jetson.GPIO as GPIO
import math
from typing import Tuple


def minute_to_degree(minutes: float) -> float:
    """Transforms minutes and decimation of minutes to degrees.
    (1° = 60 minutes)

    Args:
            minutes (float): Angular rotation in minutes

    Returns:
            float: Angle in degrees
    """
    return minutes / 60


def haversine(point_1: Tuple[float, float], point_2: Tuple[float, float]) -> float:
    """Calculates the Haversine formula relating point_1 and point_2

    Args:
            point_1 (Tuple[float, float]): Coordinates (lat, long) of point_1 in degrees
            point_2 (Tuple[float, float]): Coordinates (lat, long) of point_2 in degrees

    Returns:
            float: The great-circle distance between point_1 and point_2
    """
    delta_lat = (point_2[0] - point_1[0]) * math.pi / 180
    delta_long = (point_2[1] - point_1[1]) * math.pi / 180

    a = math.sin(delta_lat / 2) * math.sin(delta_lat / 2) + math.cos(
        point_1[0] * math.pi / 180
    ) * math.cos(point_2[0] * math.pi / 180) * math.sin(delta_long / 2) * math.sin(
        delta_long / 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371  # in km
    return R * c
