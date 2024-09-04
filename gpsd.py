import time

from gps import Sim7600Module
from coordinates import Coordinates

if __name__ == "__main__":
    board = Sim7600Module()
    board.open()

    try:
        if board.is_open:
            while 1:
                data: Coordinates
                data = board.get_gps_position()
                if data is not None:
                    print(
                        data.latitude,
                        data.latitude_indicator,
                        data.longitude,
                        data.longitude_indicator,
                    )
                time.sleep(3)

        board.close()

    except Exception as e:
        print(e)
        board.close()
