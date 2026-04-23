"""
SIM7600 module interface.
"""

from coordinates import Coordinates
from pathlib import Path
import serial
import time
from typing import Tuple


class Sim7600Module:
    """Sim7600Module interface class.

    This class is used to interface with SIM7600 Module, mainly
    for getting GPS position through AT commands.

    Serial communication is handled internally, with a configurable
    timeout. If GPS signal is weak, falls back to Location Based
    Services (LBS).

    `get_gps_position()` tries GPS up to 2 times, then falls back to LBS.
    """

    def __init__(self, address: str = "/dev/ttyUSB2", baudrate: int = 115200, timeout: int = 2):
        """Constructor for interface with SIM7600 Module.

        Args:
            address (str): Serial port. Defaults to "/dev/ttyUSB2".
            baudrate (int): Baud rate. Defaults to 115200.
            timeout (int): Serial read timeout in seconds. Defaults to 2.
        """
        self.serial_port = address
        self.baud_rate = baudrate
        self.serial_timeout = timeout
        self.serial = None
        self.is_open = False
        self.echo_enabled = True

    def send_at(self, command: str, back: str, timeout: float) -> Tuple[bool, str]:
        """Send an AT command and wait for a response.

        Args:
            command (str): AT command to send.
            back (str): Expected pattern in the response.
            timeout (float): Time to wait for response in seconds.

        Returns:
            Tuple[bool, str]:
                bool: True if expected pattern found in response, False otherwise.
                str: Decoded response buffer, or empty string on failure.
        """
        self.serial.write((command + "\r\n").encode())
        deadline = time.time() + timeout
        rec_buff = b""
        while time.time() < deadline:
            rec_buff += self.serial.read(self.serial.in_waiting or 1)
            if back.encode() in rec_buff or b"ERROR" in rec_buff:
                break
            time.sleep(0.01)

        if rec_buff:
            decoded = rec_buff.decode("utf-8", errors="replace")
            if back not in decoded:
                return (False, "")
            return (True, decoded)
        return (False, "")

    def ping(self) -> bool:
        """Ping the module by sending AT.

        Returns:
            bool: True if OK received, False otherwise.
        """
        return self.send_at("AT", "OK", 1)[0]

    def open(self) -> bool:
        """Open serial communication.

        Returns:
            bool: True if port opened successfully, False otherwise.
        """
        try:
            if not self.serial:
                self.serial = serial.Serial(
                    port=self.serial_port,
                    baudrate=self.baud_rate,
                    timeout=self.serial_timeout,
                )
            elif not self.serial.is_open:
                self.serial.open()
            self.is_open = self.serial.is_open
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            return self.is_open
        except serial.SerialException as e:
            print(f"Failed to open serial port {self.serial_port}: {e}")
            self.is_open = False
            return False

    def close(self) -> None:
        """Close the serial port."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.is_open = False

    def get_gps_position(self) -> Coordinates:
        """Get GPS position by sending AT+CGPSINFO.

        Retries up to 2 times for both comm failure and no-fix.
        Falls back to LBS if GPS is unavailable.

        Returns:
            Coordinates: Current position, or None on total failure.
        """
        response = (False, "")

        for _ in range(2):
            response = self.send_at("AT+CGPSINFO", "+CGPSINFO: ", 0.2)
            if response[0] and ",,,,,,,," not in response[1]:
                break  # Got a valid fix
        else:
            return self.get_position_from_lbs()

        if "CGPSINFO" in response[1]:
            data_str = response[1].split("+CGPSINFO: ")[1]
            data = data_str.split(",")
            return Coordinates(
                time_utc="_".join(data[4:6]),
                latitude=data[0],
                latitude_ind=data[1],
                longitude=data[2],
                longitude_ind=data[3],
                gps_status=2,
            )

        return None

    def get_position_from_lbs(self) -> Coordinates:
        """Get position using Location-Based Services (LBS).

        Less accurate than GPS (hundreds of metres to kilometres).

        Returns:
            Coordinates: Position from base station, or empty Coordinates on failure.
        """
        ret, response = self.send_at("AT+CLBS=4", "+CLBS: ", 0.6)
        if ret and "CLBS" in response:
            data_str = response.split("+CLBS: ")[1]
            data = data_str.split(",")
            if len(data) > 3:
                time_utc = (
                    "_".join(data[-2:])
                    .replace("/", "_")
                    .strip()
                )
                try:
                    uncertainty = int(data[3].strip())
                except ValueError:
                    uncertainty = 1000

                return Coordinates(
                    time_utc=time_utc,
                    latitude=data[1],
                    latitude_ind="",
                    longitude=data[2],
                    longitude_ind="",
                    from_lbs=True,
                    uncertainty=uncertainty,
                    gps_status=1,
                )

        return Coordinates(from_lbs=True)

    def reset_module(self) -> None:
        """Reset the module in case ERROR occurs."""
        self.send_at("AT+CRESET", "OK", 1)

    def enable_echo(self) -> None:
        """Enable AT command echo on the module."""
        if not self.echo_enabled:
            self.send_at("ATE1", "OK", 1)
            self.echo_enabled = True
        else:
            print("Echo already enabled.")

    def disable_echo(self) -> None:
        """Disable AT command echo on the module."""
        if self.echo_enabled:
            self.send_at("ATE0", "OK", 1)
            self.echo_enabled = False
        else:
            print("Echo already disabled.")


if __name__ == "__main__":
    board = None
    try:
        board = Sim7600Module()
        board.open()
        if board.is_open:
            gps_data = board.get_gps_position()
            print(gps_data)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        if board:
            board.close()
