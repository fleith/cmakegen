cmake_minimum_required(VERSION 3.10)
project(cmake_generator)

# set(CMAKE_CXX_COMPILER /usr/bin/clang++)
# set(CMAKE_CC_COMPILER /usr/bin/clang)
set(CMAKE_CXX_COMPILER ${CMAKE_SOURCE_DIR}/../compilers/compiler++.py)
set(CMAKE_CC_COMPILER ${CMAKE_SOURCE_DIR}/../compilers/compiler.py)

set(CMAKE_CXX_STANDARD 11)

add_executable(cmake_generator main.cpp impl0.cpp)
# target_compile_options()
