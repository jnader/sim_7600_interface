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

