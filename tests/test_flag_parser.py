"""Tests for cmakegen.flag_parser."""

from cmakegen.flag_parser import parse_args


def test_compile_only():
    result = parse_args(["-c", "main.cpp"])
    assert result["compile_only"] is True


def test_output():
    result = parse_args(["-o", "main.o", "-c", "main.cpp"])
    assert result["output"] == "main.o"


def test_std():
    result = parse_args(["-std=c++17", "-c", "main.cpp"])
    assert result["std"] == "c++17"


def test_include_dirs_joined():
    result = parse_args(["-I/usr/include/foo", "-c", "main.cpp"])
    assert result["include_dirs"] == ["/usr/include/foo"]


def test_include_dirs_separated():
    result = parse_args(["-I", "/usr/include/bar", "-c", "main.cpp"])
    assert result["include_dirs"] == ["/usr/include/bar"]


def test_defines_joined():
    result = parse_args(["-DDEBUG", "-DVERSION=2", "-c", "main.cpp"])
    assert result["defines"] == ["DEBUG", "VERSION=2"]


def test_defines_separated():
    result = parse_args(["-D", "DEBUG", "-c", "main.cpp"])
    assert result["defines"] == ["DEBUG"]


def test_lib_dirs():
    result = parse_args(["-L/usr/lib", "-L", "/opt/lib", "main.o"])
    assert result["lib_dirs"] == ["/usr/lib", "/opt/lib"]


def test_libraries():
    result = parse_args(["-lpthread", "-l", "m", "main.o"])
    assert result["libraries"] == ["pthread", "m"]


def test_optimization():
    for level in ["0", "1", "2", "3", "s", "g"]:
        result = parse_args([f"-O{level}", "-c", "main.cpp"])
        assert result["optimization"] == level


def test_warnings():
    result = parse_args(["-Wall", "-Wextra", "-Werror", "-c", "main.cpp"])
    assert result["warnings"] == ["all", "extra", "error"]


def test_debug():
    result = parse_args(["-g", "-c", "main.cpp"])
    assert result["debug"] is True


def test_no_debug():
    result = parse_args(["-c", "main.cpp"])
    assert result["debug"] is False


def test_pic():
    result = parse_args(["-fPIC", "-c", "main.cpp"])
    assert result["pic"] is True

    result = parse_args(["-fpic", "-c", "main.cpp"])
    assert result["pic"] is True


def test_pthread():
    result = parse_args(["-pthread", "-c", "main.cpp"])
    assert result["pthread"] is True


def test_linker_flags():
    result = parse_args(["-Wl,-search_paths_first", "-Wl,-headerpad_max_install_names", "main.o"])
    assert result["linker_flags"] == ["-Wl,-search_paths_first", "-Wl,-headerpad_max_install_names"]


def test_source_files():
    result = parse_args(["-c", "main.cpp", "impl0.cc", "util.c", "extra.cxx"])
    assert result["source_files"] == ["main.cpp", "impl0.cc", "util.c", "extra.cxx"]


def test_object_files():
    result = parse_args(["main.o", "impl0.o", "-o", "program"])
    assert result["object_files"] == ["main.o", "impl0.o"]


def test_other_flags():
    result = parse_args(["-fno-exceptions", "-c", "main.cpp"])
    assert result["other_flags"] == ["-fno-exceptions"]


def test_combined():
    args = [
        "-g", "-std=gnu++11", "-O2", "-Wall", "-Wextra",
        "-I/usr/include/foo", "-DDEBUG", "-DVERSION=2",
        "-fPIC", "-pthread", "-fno-exceptions",
        "-c", "-o", "main.o", "main.cpp",
    ]
    result = parse_args(args)
    assert result["debug"] is True
    assert result["std"] == "gnu++11"
    assert result["optimization"] == "2"
    assert result["warnings"] == ["all", "extra"]
    assert result["include_dirs"] == ["/usr/include/foo"]
    assert result["defines"] == ["DEBUG", "VERSION=2"]
    assert result["pic"] is True
    assert result["pthread"] is True
    assert result["other_flags"] == ["-fno-exceptions"]
    assert result["compile_only"] is True
    assert result["output"] == "main.o"
    assert result["source_files"] == ["main.cpp"]
