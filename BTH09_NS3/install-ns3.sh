#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y build-essential python3 python3-dev git cmake ninja-build pkg-config libsqlite3-dev libxml2-dev qtbase5-dev qt5-qmake libqt5svg5-dev
cd "$HOME"
test ! -e ns-3.43 || { echo 'ns-3.43 already exists: inspect it before rerunning.'; exit 1; }
git clone --depth 1 --branch ns-3.43 https://gitlab.com/nsnam/ns-3-dev.git ns-3.43
cd ns-3.43
./ns3 configure --enable-examples --enable-tests
./ns3 build -j 2
./ns3 run hello-simulator
cd "$HOME"
if [[ ! -e netanim ]]; then git clone https://gitlab.com/nsnam/netanim.git; fi
cd netanim
# Use CMake when supported by the checked-out NetAnim source.
if [[ -f CMakeLists.txt ]]; then cmake -S . -B build; cmake --build build -j 2;
else qmake NetAnim.pro; make -j2; fi
