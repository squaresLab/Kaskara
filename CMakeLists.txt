cmake_minimum_required(VERSION 2.0)

project(Bond CXX)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
find_package(Clang REQUIRED)

add_subdirectory(src)
