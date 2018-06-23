#!/usr/bin/env python3
import sys
import subprocess


# -std=<value>            Language standard to compile for
lang_std = {"-std=c++11":11, 
"-std=gnu++11":11,
"-std=c++98":98,
"-std=gnu++98":98,
"-std=C++14":14,
"-std=gnu++14":14}

standard = 98

arguments = sys.argv[1:]
for arg in arguments:
	if arg in lang_std:
		standard = lang_std[arg]

cmake_file = '''
cmake_minimum_required(VERSION 3.10)
project({proj_name})

set(CMAKE_CXX_STANDARD {cpp_version})

add_executable({proj_name} {src_files})
'''.format(proj_name="project", cpp_version=standard, src_files="abc")

print(cmake_file)

print("My compiler++")
print(sys.argv)

subprocess.run(["clang++"] + arguments, stdout=subprocess.PIPE)

