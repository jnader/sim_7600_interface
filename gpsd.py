import time

from gps import Sim7600Module

if __name__ == "__main__":
    board = Sim7600Module()
    board.open()

    try:
        if board.is_open:
            while 1:
                data = board.get_gps_position()
                if data[0] != "":
                    print(data)
                time.sleep(3)

        board.close()

    except Exception as e:
        print(e)
        board.close()
