"""Integration tests simulating full multi-file builds."""

import os
import tempfile

from cmakegen.flag_parser import parse_args
from cmakegen.invocation_log import clear_log, log_invocation, read_invocations
from cmakegen.cmake_generator import generate_cmake


def test_full_one_file_build(tmp_path):
    """Simulate the one-file build from cmake_generator.txt end-to-end."""
    log_path = str(tmp_path / "build.jsonl")

    # Compile step
    compile_args = ["-g", "-std=gnu++11",
                    "-o", "CMakeFiles/cmake_generator.dir/main.cpp.o",
                    "-c", "/Users/alvaro/ClionProjects/cmake_generator/main.cpp"]
    inv1 = parse_args(compile_args)
    log_invocation(log_path, inv1)

    # Link step
    link_args = ["-g", "-Wl,-search_paths_first", "-Wl,-headerpad_max_install_names",
                 "CMakeFiles/cmake_generator.dir/main.cpp.o", "-o", "cmake_generator"]
    inv2 = parse_args(link_args)
    log_invocation(log_path, inv2)

    # Generate
    invocations = read_invocations(log_path)
    result = generate_cmake(invocations)

    assert "cmake_minimum_required(VERSION 3.10)" in result
    assert "project(cmake_generator)" in result
    assert "set(CMAKE_CXX_STANDARD 11)" in result
    assert "add_executable(cmake_generator main.cpp)" in result


def test_full_two_file_build(tmp_path):
    """Simulate the two-file build from cmake_generator.txt end-to-end."""
    log_path = str(tmp_path / "build.jsonl")

    # Compile steps
    compile1 = parse_args(["-g", "-std=gnu++11",
                           "-o", "CMakeFiles/cmake_generator.dir/main.cpp.o",
                           "-c", "/Users/alvaro/ClionProjects/cmake_generator/main.cpp"])
    compile2 = parse_args(["-g", "-std=gnu++11",
                           "-o", "CMakeFiles/cmake_generator.dir/impl0.cpp.o",
                           "-c", "/Users/alvaro/ClionProjects/cmake_generator/impl0.cpp"])
    log_invocation(log_path, compile1)
    log_invocation(log_path, compile2)

    # Link step
    link = parse_args(["-g", "-Wl,-search_paths_first", "-Wl,-headerpad_max_install_names",
                       "CMakeFiles/cmake_generator.dir/main.cpp.o",
                       "CMakeFiles/cmake_generator.dir/impl0.cpp.o",
                       "-o", "cmake_generator"])
    log_invocation(log_path, link)

    # Generate
    invocations = read_invocations(log_path)
    result = generate_cmake(invocations)

    assert "cmake_minimum_required(VERSION 3.10)" in result
    assert "project(cmake_generator)" in result
    assert "set(CMAKE_CXX_STANDARD 11)" in result
    assert "main.cpp" in result
    assert "impl0.cpp" in result


def test_build_with_libraries(tmp_path):
    """Simulate a build with library dependencies."""
    log_path = str(tmp_path / "build.jsonl")

    compile_inv = parse_args(["-g", "-std=c++17", "-O2", "-Wall",
                              "-I/usr/include/boost", "-DUSE_BOOST",
                              "-c", "-o", "main.o", "main.cpp"])
    log_invocation(log_path, compile_inv)

    link_inv = parse_args(["main.o", "-o", "myapp",
                           "-L/usr/lib", "-lboost_system", "-lpthread"])
    log_invocation(log_path, link_inv)

    invocations = read_invocations(log_path)
    result = generate_cmake(invocations)

    assert "project(myapp)" in result
    assert "set(CMAKE_CXX_STANDARD 17)" in result
    assert "target_include_directories(myapp PRIVATE /usr/include/boost)" in result
    assert "target_compile_definitions(myapp PRIVATE USE_BOOST)" in result
    assert "target_link_libraries(myapp PRIVATE boost_system pthread)" in result
    assert "target_link_directories(myapp PRIVATE /usr/lib)" in result
