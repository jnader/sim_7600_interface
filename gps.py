"""
SIM7600 module interface.
"""

from coordinates import Coordinates
from pathlib import Path
import serial
import time
from typing import Tuple
from utils import nmea_to_coordinates, haversine


class Sim7600Module:
    """Sim7600Module interface class."""

    def __init__(self, address: Path = "/dev/ttyUSB2", baudrate: int = 115200):
        """Constructor

        Args:
            address (Path, optional): serial port. Defaults to "/dev/ttyUSB2".
            baudrate (int, optional): baud rate. Defaults to 115200.
        """
        self.serial_port = address
        self.baud_rate = baudrate
        self.reference_position = (None, None)
        self.serial = None
        self.is_open = False
        self.echo_enabled = True

    def send_at(self, command: str) -> Tuple[bool, str]:
        """Send command as AT command.

        Args:
                command (str): AT command

        Returns:
                bool: True if received OK as response, False otherwise
        """
        rec_buff = ""
        # self.serial.reset_output_buffer()
        self.serial.write((command + "\r\n").encode())
        timeout = time.time() + 3.0
        # self.serial.reset_input_buffer()
        while self.serial.inWaiting() or time.time() - timeout < 0.0:
            if self.serial.inWaiting() > 0:
                try:
                    rec_buff = self.serial.read(self.serial.inWaiting())
                    break
                except Exception as e:
                    break
        if rec_buff != "":
            if "OK" not in rec_buff.decode():
                return [False, rec_buff.decode()]
            else:
                return [True, rec_buff.decode()]
        return [False, rec_buff]

    def ping(self) -> bool:
        """Ping to check if the module is reachable by sending `AT`.

        Returns:
            bool: True if `OK` received, False otherwise
        """
        return self.send_at("AT")[0]

    def open(self) -> None:
        """Open serial communication"""
        if not self.serial:
            self.serial = serial.Serial(port=self.serial_port, baudrate=self.baud_rate)
            self.is_open = self.serial.is_open
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
        else:
            if self.serial.is_open:
                print("Closing already open serial")
                self.serial.close()
                self.serial.open()

    def close(self) -> None:
        """Close serial port.

        Returns:
            bool: True if disconnect succeeded, False otherwise
        """
        if self.serial.is_open:
            self.serial.close()

    def get_gps_position(self) -> Coordinates:
        """Get GPS (latitude, longitude positions) by sending `AT+CGPSINFO`

        Returns:
            Coordinates: (time_utc, latitude, longitude)
        """
        response = [False, None]
        while not response[0]:
            response = self.send_at("AT+CGPSINFO")
            if response[1] and ",,,,,,,," in response[1]:
                print("GPS not ready")
                response = [False, None]
        if response[0] and "CGPSINFO" in response[1]:
            data_str = response[1].split("+CGPSINFO: ")[1]
            data = data_str.split(",")
            return Coordinates(
                time_utc="_".join(data[4:6]),
                latitude=data[0],
                latitude_ind=data[1],
                longitude=data[2],
                longitude_ind=data[3],
            )
        return None

    def get_distance_to(self, position: Tuple[float, float]) -> float:
        """Gets distance between current GPS position and some `position`

        Args:
            position (Tuple[float, float]): Position to calculate the distance to in degrees.

        Returns:
            float: Distance from module to `position`
        """
        return haversine(self.get_gps_position(), position)

    def enable_echo(self):
        """Enables echo on the board. This will enable echoing the result of AT commands."""
        if self.echo_enabled:
            print("echo already enabled...")
        else:
            self.send_at("ATE")


if __name__ == "__main__":
    board = Sim7600Module()
    board.open()
    if board.is_open:
        print(board.get_gps_position())

        board.close()

    # point_1_nmea = (2508.472, 5523.562)
    # point_2_nmea = (2505.166, 05531.262)
    # point_1 = nmea_to_coordinates(point_1_nmea)
    # point_2 = nmea_to_coordinates(point_2_nmea)

    # print(point_1, point_2)
    # print(haversine(point_1, point_2))
