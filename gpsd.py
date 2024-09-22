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
                print(board.gps_status, data)
                time.sleep(1)

        board.close()

    except KeyboardInterrupt as e:
        board.close()
