# cmakegen

A tool that intercepts C/C++ compiler invocations during a build and generates a `CMakeLists.txt` from the captured flags and source files.

## How it works

1. **Proxy compilers** (`compilers/compiler.py` and `compilers/compiler++.py`) replace `cc`/`clang++` in your build system. They parse and log every compiler invocation, then forward the call to the real compiler.
2. After the build completes, run `python -m cmakegen generate` to produce a `CMakeLists.txt` from the aggregated invocations.

## Usage

### 1. Configure your build to use the proxy compilers

Point your build system at the proxy scripts. For example, with CMake:

```cmake
set(CMAKE_CXX_COMPILER /path/to/cmakegen/compilers/compiler++.py)
set(CMAKE_C_COMPILER /path/to/cmakegen/compilers/compiler.py)
```

Or with environment variables:

```bash
export CC=/path/to/cmakegen/compilers/compiler.py
export CXX=/path/to/cmakegen/compilers/compiler++.py
```

### 2. Run your build

```bash
make        # or cmake --build, ninja, etc.
```

Each compiler call is logged to `.cmakegen_log.jsonl` (override with `CMAKEGEN_LOG` env var).

### 3. Generate CMakeLists.txt

```bash
python -m cmakegen generate             # print to stdout
python -m cmakegen generate -o CMakeLists.txt   # write to file
python -m cmakegen clear                # reset the log
```

## Supported flags

| Flag | Description |
|------|-------------|
| `-c` | Compile-only (vs link step) |
| `-o <file>` | Output file / target name |
| `-std=<val>` | C/C++ standard |
| `-I<dir>` | Include directories |
| `-D<macro>` | Preprocessor defines |
| `-L<dir>` | Library search paths |
| `-l<lib>` | Link libraries |
| `-O0`/`-O1`/`-O2`/`-O3`/`-Os`/`-Og` | Optimization level |
| `-W<warning>` | Warning flags |
| `-g` | Debug info |
| `-fPIC`/`-fpic` | Position-independent code |
| `-pthread` | Threading support |
| `-Wl,<flags>` | Linker flags |

## Running tests

```bash
python -m pytest tests/ -v
```

## License

MIT
