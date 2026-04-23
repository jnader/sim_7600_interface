import time
from gps import Sim7600Module
from coordinates import Coordinates


if __name__ == "__main__":
    board = Sim7600Module()
    board.open()
    try:
        if board.is_open:
            while True:
                data: Coordinates = board.get_gps_position()
                print(data)
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing serial communication.")
    finally:
        board.close()
