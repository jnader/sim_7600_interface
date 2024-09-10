"""
SIM7600 module interface.
"""

from coordinates import Coordinates
from pathlib import Path
import serial
import time
from typing import Tuple


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

        command_sliced = command.split("+")
        pattern = ""
        if len(command_sliced) > 1:
            pattern = command_sliced[-1].split("=")[0]

        rec_buff = ""
        self.serial.write((command + "\r\n").encode())
        timeout = time.time() + 3.0
        while self.serial.in_waiting or time.time() - timeout < 0.0:
            if self.serial.in_waiting > 0:
                try:
                    rec_buff = self.serial.read(self.serial.in_waiting)
                    if pattern in rec_buff.decode():
                        break
                except Exception as e:
                    print(pattern, e)
        if rec_buff != "":
            if pattern not in rec_buff.decode():
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
        counter = 0
        while counter < 2:
            response = self.send_at("AT+CGPSINFO")
            if response[0]:
                if ",,,,,,,," in response[1]:
                    return self.get_position_from_lbs()
                else:
                    break
            counter += 1

        if counter == 2:
            return self.get_position_from_lbs()

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

    def get_position_from_lbs(self) -> Coordinates:
        """Gets position using Location-Based-Services (LBS).
        The position tends to have less accuracy than GPS, ranging
        from hundreds of meters to kilometers.

        Returns:
            Coordinates: Coordinates of the base station.
        """
        ret, response = self.send_at("AT+CLBS=4")
        if ret and "CLBS" in response:
            data_str = response.split("+CLBS: ")[1]
            data = data_str.split(",")
            time_utc = (
                "_".join(data[-2:])
                .replace("/", "_")
                .replace("\r", "")
                .replace("\n", "")
            )
            return Coordinates(
                time_utc=time_utc,
                latitude=data[1],
                latitude_ind="",
                longitude=data[2],
                longitude_ind="",
                from_lbs=True,
            )

    def enable_echo(self):
        """Enables echo on the board. This will enable echoing the result of AT commands."""
        if self.echo_enabled:
            print("echo already enabled...")
        else:
            self.send_at("ATE")


if __name__ == "__main__":
    board = None
    try:
        board = Sim7600Module()
        board.open()
        if board.is_open:
            gps_data: Coordinates
            gps_data = board.get_gps_position()
            print(gps_data)

            board.close()

    except KeyboardInterrupt as e:
        if board and board.is_open:
            print("\nClosing serial communication.")
            board.close()
