[![CI](https://github.com/dperl-dls/rtc6-fastcs/actions/workflows/ci.yml/badge.svg)](https://github.com/dperl-dls/rtc6-fastcs/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/dperl-dls/rtc6-fastcs/branch/main/graph/badge.svg)](https://codecov.io/gh/dperl-dls/rtc6-fastcs)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# rtc6_fastcs

FastCS IOC for the ScanLab RTC6 Ethernet laser controller

Source          | <https://github.com/dperl-dls/rtc6-fastcs>
:---:           | :---:
Docker          | `docker run ghcr.io/dperl-dls/rtc6-fastcs:latest`
Releases        | <https://github.com/dperl-dls/rtc6-fastcs/releases>

# updating the bindings module

To update the bindings, in the devcontainer and with the virtual env activated, execute:

```bash
cd src/rtc6_fastcs/bindings
mkdir build # if necessary
cd build
cmake ..
make
cd ../../../..
pybind11-stubgen rtc6_fastcs.bindings.rtc6_bindings -o src
ruff format .
```

# using devcontainer on RH7

manually build the container with ``
