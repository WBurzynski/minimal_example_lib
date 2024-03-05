cmake_minimum_required(VERSION 3.22)
project(minimal_example_lib)

set(CMAKE_CXX_STANDARD 20)

#find_package(Boost CONFIGS REQUIRED)
find_package(fmt CONFIGS REQUIRED)

add_subdirectory(a)
add_subdirectory(b)
add_subdirectory(c)
