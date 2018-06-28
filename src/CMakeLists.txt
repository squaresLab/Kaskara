include(GNUInstallDirs)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -ggdb")

include_directories(${CLANG_INCLUDE_DIRS})
add_definitions(${CLANG_DEFINITIONS})
add_definitions(-std=c++17)

add_executable(bond
  main.cpp
)
