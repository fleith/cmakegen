#!/usr/bin/env bash
# Full round-trip test: proxy compile -> generate CMakeLists.txt -> cmake rebuild -> run
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPILER="$ROOT_DIR/compilers/compiler++.py"

cd "$SCRIPT_DIR"

export PYTHONPATH="$ROOT_DIR"
export CMAKEGEN_LOG="$SCRIPT_DIR/.cmakegen_log.jsonl"

# On Windows (MSYS/MinGW/Git Bash), set up MSVC environment for clang++
setup_windows_env() {
    # Find the latest MSVC toolset
    local vs_base="/c/Program Files/Microsoft Visual Studio"
    local msvc_inc
    msvc_inc=$(find "$vs_base" -maxdepth 8 -path "*/VC/Tools/MSVC/*/include" -type d 2>/dev/null | sort -V | tail -1)
    [ -z "$msvc_inc" ] && { echo "ERROR: MSVC include dir not found"; exit 1; }

    local msvc_base
    msvc_base="$(dirname "$msvc_inc")"

    # Find the latest Windows SDK ucrt include
    local sdk_ucrt
    sdk_ucrt=$(find "/c/Program Files (x86)/Windows Kits/10/Include" -maxdepth 2 -name "ucrt" -type d 2>/dev/null | sort -V | tail -1)
    [ -z "$sdk_ucrt" ] && { echo "ERROR: Windows SDK ucrt not found"; exit 1; }

    local sdk_ver
    sdk_ver="$(basename "$(dirname "$sdk_ucrt")")"
    local sdk_base="/c/Program Files (x86)/Windows Kits/10"

    # Set include paths (env vars, not CLI flags — won't be logged by proxy)
    export CPLUS_INCLUDE_PATH="$msvc_inc:$sdk_ucrt"

    # Set library paths for the MSVC linker (uses Windows-style paths)
    local msvc_base_win sdk_base_win
    msvc_base_win="$(cygpath -w "$msvc_base")"
    sdk_base_win="$(cygpath -w "$sdk_base")"
    export LIB="$msvc_base_win\\lib\\x64;$sdk_base_win\\Lib\\$sdk_ver\\ucrt\\x64;$sdk_base_win\\Lib\\$sdk_ver\\um\\x64"

    # Ensure LLVM, CMake, and build tools are on PATH
    [ -d "/c/Program Files/LLVM/bin" ] && export PATH="/c/Program Files/LLVM/bin:$PATH"
    [ -d "/c/Program Files/CMake/bin" ] && export PATH="/c/Program Files/CMake/bin:$PATH"
    # Add VS-bundled Ninja if no other build tool is available
    if ! command -v ninja &>/dev/null && ! command -v make &>/dev/null; then
        local ninja_dir
        ninja_dir=$(find "$vs_base" -name "ninja.exe" -type f 2>/dev/null | head -1)
        [ -n "$ninja_dir" ] && export PATH="$(dirname "$ninja_dir"):$PATH"
    fi

    echo "==> Windows environment configured (MSVC $sdk_ver)"
}

case "$(uname -s)" in
    MSYS*|MINGW*|CYGWIN*) setup_windows_env ;;
esac

# Clean previous artifacts
rm -rf build *.o example_app example_app.exe CMakeLists.txt

# 1. Clear the invocation log
python -m cmakegen clear --log "$CMAKEGEN_LOG"
echo "==> Log cleared"

# 2. Compile each source with the proxy compiler
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
CMAKE_ARGS=(..)
# On Windows, specify the full compiler path and use Ninja if available
if [[ "$(uname -s)" == MSYS* || "$(uname -s)" == MINGW* || "$(uname -s)" == CYGWIN* ]]; then
    CLANGXX_PATH="$(cygpath -w "$(command -v clang++)")"
    CMAKE_ARGS+=(-DCMAKE_CXX_COMPILER="$CLANGXX_PATH")
    if command -v ninja &>/dev/null; then
        CMAKE_ARGS+=(-G Ninja)
    else
        CMAKE_ARGS+=(-G "Unix Makefiles")
    fi
fi
cmake "${CMAKE_ARGS[@]}"
cmake --build .
echo "==> CMake build succeeded"

# 6. Run the binary and verify output
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
