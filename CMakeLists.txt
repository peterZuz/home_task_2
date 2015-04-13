cmake_minimum_required(VERSION 3.0)

set(CMAKE_VERBOSE_MAKEFILE on)

find_package(PythonLibs 3.2 REQUIRED)

include_directories(${PYTHON_INCLUDE_DIRS})

python_add_module(c_module c_module.cpp)

target_link_libraries(c_module ${PYTHON_LIBRARIES})