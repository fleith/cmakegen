#!/usr/bin/env bash
# Full round-trip test: proxy compile -> generate CMakeLists.txt -> cmake rebuild -> run
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPILER="$ROOT_DIR/compilers/compiler++.py"

cd "$SCRIPT_DIR"

# Clean previous artifacts
rm -rf build *.o example_app CMakeLists.txt

# 1. Clear the invocation log
export CMAKEGEN_LOG="$SCRIPT_DIR/.cmakegen_log.jsonl"
python -m cmakegen clear --log "$CMAKEGEN_LOG"
echo "==> Log cleared"

# 2. Compile each source with the proxy compiler
export PYTHONPATH="$ROOT_DIR"
python "$COMPILER" -std=c++17 -g -c main.cpp -o main.o
python "$COMPILER" -std=c++17 -g -c mathutils.cpp -o mathutils.o
echo "==> Compiled source files"

# 3. Link object files with the proxy compiler
python "$COMPILER" main.o mathutils.o -o example_app
echo "==> Linked example_app"

# 4. Generate CMakeLists.txt from the log
python -m cmakegen generate --log "$CMAKEGEN_LOG" -o CMakeLists.txt
echo "==> Generated CMakeLists.txt"
cat CMakeLists.txt

# 5. Rebuild with the generated CMake
mkdir -p build
cd build
cmake ..
cmake --build .
echo "==> CMake build succeeded"

# 6. Run the binary and verify output
# The binary name matches the target in the generated CMakeLists.txt
if [ -f example_app ]; then
    BIN=./example_app
elif [ -f example_app.exe ]; then
    BIN=./example_app.exe
elif [ -f Debug/example_app.exe ]; then
    BIN=./Debug/example_app.exe
elif [ -f Release/example_app.exe ]; then
    BIN=./Release/example_app.exe
else
    echo "ERROR: Could not find built binary"
    exit 1
fi

OUTPUT=$($BIN)
echo "$OUTPUT"

echo "$OUTPUT" | grep -q "factorial(5) = 120" || { echo "FAIL: factorial output incorrect"; exit 1; }
echo "$OUTPUT" | grep -q "fibonacci(7) = 13" || { echo "FAIL: fibonacci output incorrect"; exit 1; }

echo "==> All checks passed!"
