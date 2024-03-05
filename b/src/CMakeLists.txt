add_library(b b.cpp ../include/b/b.hpp)

target_include_directories(b PUBLIC ../include)

target_link_libraries(b PUBLIC fmt::fmt)
