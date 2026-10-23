#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
if [[ "$(uname -s)" == "Darwin" ]]; then
  c++ -O3 -dynamiclib -std=c++17 hungarian_bridge.cpp -o build/libhungarian.dylib
else
  c++ -O3 -fPIC -shared -std=c++17 hungarian_bridge.cpp -o build/libhungarian.so
fi
echo "Native backend built. Run unit tests to verify equivalence."
