#!/bin/bash


if [ ! -f RTC6-1.19.1.zip ]; then
    echo "Fetching file"
    curl -O https://www.scanlab.de/sites/default/files/2024-11/RTC6-1.19.1.zip
else
    echo "Library zip file already exists"
fi
echo "Unzipping file"
unzip RTC6-1.19.1.zip
echo "Installing library"
dpkg -i "RTC6-1.19.1/RTC6 Files/Linux/debian-bookworm/rtc6-devel_0.1.48-1_amd64.deb"
mkdir -p rtc6_files
cp -r "RTC6-1.19.1/RTC6 Files/Program Files" rtc6_files/program_files
cp -r "RTC6-1.19.1/Correction Files" rtc6_files/correction_files
rm -rf RTC6-1.19.1/
