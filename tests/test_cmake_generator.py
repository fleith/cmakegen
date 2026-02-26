"""Tests for cmakegen.cmake_generator."""

from cmakegen.cmake_generator import generate_cmake
from cmakegen.flag_parser import parse_args


def test_single_source():
    invocations = [
        {
            "source_files": ["main.cpp"],
            "object_files": [],
            "output": "main.o",
            "std": "c++17",
            "include_dirs": [],
            "defines": [],
            "lib_dirs": [],
            "libraries": [],
            "optimization": None,
            "warnings": [],
            "debug": False,
            "pic": False,
            "pthread": False,
            "compile_only": True,
            "linker_flags": [],
            "other_flags": [],
        },
        {
            "source_files": [],
            "object_files": ["main.o"],
            "output": "myapp",
            "std": None,
            "include_dirs": [],
            "defines": [],
            "lib_dirs": [],
            "libraries": [],
            "optimization": None,
            "warnings": [],
            "debug": False,
            "pic": False,
            "pthread": False,
            "compile_only": False,
            "linker_flags": [],
            "other_flags": [],
        },
    ]
    result = generate_cmake(invocations)
    assert "project(myapp)" in result
    assert "add_executable(myapp main.cpp)" in result
    assert "set(CMAKE_CXX_STANDARD 17)" in result


def test_multiple_sources():
    invocations = [
        parse_args(["-g", "-std=gnu++11", "-o", "CMakeFiles/cmake_generator.dir/main.cpp.o", "-c", "main.cpp"]),
        parse_args(["-g", "-std=gnu++11", "-o", "CMakeFiles/cmake_generator.dir/impl0.cpp.o", "-c", "impl0.cpp"]),
        parse_args(["CMakeFiles/cmake_generator.dir/main.cpp.o", "CMakeFiles/cmake_generator.dir/impl0.cpp.o", "-o", "cmake_generator"]),
    ]
    result = generate_cmake(invocations)
    assert "project(cmake_generator)" in result
    assert "main.cpp" in result
    assert "impl0.cpp" in result


def test_with_libraries():
    invocations = [
        parse_args(["-c", "-std=c++11", "-o", "main.o", "main.cpp"]),
        parse_args(["main.o", "-o", "myapp", "-lpthread", "-lm"]),
    ]
    result = generate_cmake(invocations)
    assert "target_link_libraries(myapp PRIVATE pthread m)" in result


def test_with_includes():
    invocations = [
        parse_args(["-c", "-I/usr/include/foo", "-I/usr/include/bar", "-o", "main.o", "main.cpp"]),
        parse_args(["main.o", "-o", "myapp"]),
    ]
    result = generate_cmake(invocations)
    assert "target_include_directories(myapp PRIVATE /usr/include/foo /usr/include/bar)" in result


def test_with_defines():
    invocations = [
        parse_args(["-c", "-DDEBUG", "-DVERSION=2", "-o", "main.o", "main.cpp"]),
        parse_args(["main.o", "-o", "myapp"]),
    ]
    result = generate_cmake(invocations)
    assert "target_compile_definitions(myapp PRIVATE DEBUG VERSION=2)" in result


def test_one_file_from_cmake_generator_txt():
    """Test the 'one file' example from cmake_generator.txt."""
    invocations = [
        parse_args(["-g", "-std=gnu++11", "-o", "CMakeFiles/cmake_generator.dir/main.cpp.o", "-c",
                     "/Users/alvaro/ClionProjects/cmake_generator/main.cpp"]),
        parse_args(["-g", "-Wl,-search_paths_first", "-Wl,-headerpad_max_install_names",
                     "CMakeFiles/cmake_generator.dir/main.cpp.o", "-o", "cmake_generator"]),
    ]
    result = generate_cmake(invocations)
    assert "cmake_minimum_required(VERSION 3.10)" in result
    assert "project(cmake_generator)" in result
    assert "set(CMAKE_CXX_STANDARD 11)" in result
    assert "add_executable(cmake_generator main.cpp)" in result


def test_two_files_from_cmake_generator_txt():
    """Test the 'two files' example from cmake_generator.txt."""
    invocations = [
        parse_args(["-g", "-std=gnu++11", "-o", "CMakeFiles/cmake_generator.dir/main.cpp.o", "-c",
                     "/Users/alvaro/ClionProjects/cmake_generator/main.cpp"]),
        parse_args(["-g", "-std=gnu++11", "-o", "CMakeFiles/cmake_generator.dir/impl0.cpp.o", "-c",
                     "/Users/alvaro/ClionProjects/cmake_generator/impl0.cpp"]),
        parse_args(["-g", "-Wl,-search_paths_first", "-Wl,-headerpad_max_install_names",
                     "CMakeFiles/cmake_generator.dir/main.cpp.o", "CMakeFiles/cmake_generator.dir/impl0.cpp.o",
                     "-o", "cmake_generator"]),
    ]
    result = generate_cmake(invocations)
    assert "cmake_minimum_required(VERSION 3.10)" in result
    assert "project(cmake_generator)" in result
    assert "set(CMAKE_CXX_STANDARD 11)" in result
    # Both source files should appear
    assert "main.cpp" in result
    assert "impl0.cpp" in result


def test_compile_options():
    invocations = [
        parse_args(["-g", "-O2", "-Wall", "-Wextra", "-fno-exceptions", "-c", "-o", "main.o", "main.cpp"]),
        parse_args(["main.o", "-o", "myapp"]),
    ]
    result = generate_cmake(invocations)
    assert "target_compile_options(myapp PRIVATE -Wall -Wextra -g -O2 -fno-exceptions)" in result


def test_c_standard():
    invocations = [
        parse_args(["-std=c11", "-c", "-o", "main.o", "main.c"]),
        parse_args(["main.o", "-o", "myapp"]),
    ]
    result = generate_cmake(invocations)
    assert "set(CMAKE_C_STANDARD 11)" in result
