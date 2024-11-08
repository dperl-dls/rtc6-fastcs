#!/bin/bash

cd src/rtc6_fastcs/bindings
mkdir -p build # if necessary
cd build
cmake ..
make
cd ../../../..
pybind11-stubgen rtc6_fastcs.bindings.rtc6_bindings -o src
ruff format .
