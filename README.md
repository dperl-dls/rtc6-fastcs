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

# developing in the container over ssh

At diamond the default devcontainer settings result in some permission issues when run over ssh, but you can build the container and develop in it manually

manually build the container with `podman build -t rtc6-fastcs-dev --target=developer .`
and run it with `podman run -it --net=host --security-opt=label=disable --mount=type=bind,source=/scratch/ziq44869/rtc6-fastcs/,destination=/workspace rtc6-fastcs-dev`
then connect vscode to the laser lab workstation with `remote:ssh` and attach to the running container from the `remote:containers` view
the first time for a running container you will need to install the relevant extensions, run `pip install -e .[dev]`, and `rtc6-fastcs install-library` or the `install-library.sh` script from the repo
when everything is set up, `test_connect()` from `test_bindings.py` should pass

# notes

- fastcs doesn't completely work for python 3.12 but fails silently so this project will need to be moved to 3.11
