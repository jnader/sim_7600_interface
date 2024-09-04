# Install

```
sudo apt update
sudo apt upgrade
sudo apt install libgdal-dev
```

```
pip3 install -r requirements.txt
```

# Known issues

- When importing numpy, you may get the following error:
```
python3 -c "import numpy"
Illegal instruction (core dumped)
```

To counter this error, do:

```
OPENBLAS_CORETYPE=ARMV8 python3 -c "import numpy"
```

# Usage
- To get only one gps position, the following code should be ran:
```
from gps import Sim7600Module
board = Sim7600Module()
board.open()
if board.is_open:
    gps_data: Coordinates
    gps_data = board.get_gps_position()
    print(gps_data)

    board.close()
```

# Example
- To continuously query GPS position, use the following example:
```
OPENBLAS_CORETYPE=ARMV8 python3 gpsd.py
```
