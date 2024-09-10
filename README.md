This projects is used to interface with SIM7600G-H LTE module.
The main purpose is get the GPS position from this module and
detect if it lies inside/outside of a GIS-zone.

# Description
Using SIM7600 LTE module, we try to use AT commands to get GPS position. If no position is fixed with standalone GPS, the position will use Location Based Services (LBS) from telecom operator.
The project is under developement.

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
- To get GPS position once in an example, use the following example:
```
sudo OPENBLAS_CORETYPE=ARMV8 python3 gps.py
```

- To continuously query GPS position, use the following example:
```
sudo OPENBLAS_CORETYPE=ARMV8 python3 gpsd.py
```

- To run `main.py`, you need to have the folder containing exported files in the same directory of the project.
```
sudo OPENBLAS_CORETYPE=ARMV8 python3 main.py
```
This example will currently search for `Blue_Line` folder. If not it will fail.
